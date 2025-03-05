from datetime import UTC, datetime

from inventory.database import database


async def get_items():
    query = """
        SELECT
            id,
            name,
            total_qty,
            borrowed_qty,
            (total_qty - borrowed_qty) AS available_qty
        FROM items
        ORDER BY name
    """
    return await database.fetch_all(query)


async def get_item(id: int):
    query = """
        SELECT
            id,
            name,
            total_qty,
            borrowed_qty,
            (total_qty - borrowed_qty) AS available_qty
        FROM items
        WHERE id = :id
    """
    return await database.fetch_one(query, values={"id": id})


async def edit_item(
    id: int,
    name: str | None = None,
    total_qty: int | None = None,
    borrowed_qty: int | None = None,
):
    # First check if the item exists
    item = await get_item(id)
    if not item:
        return None

    # Determine which fields to update
    updates = []
    values = {"id": id}

    if name is not None:
        updates.append("name = :name")
        values["name"] = name

    if total_qty is not None:
        if total_qty < 0:
            raise ValueError("Total quantity cannot be negative")

        # If we're also updating borrowed_qty, we'll check constraints after setting both values
        # Only updating total_qty, check against existing borrowed_qty
        if borrowed_qty is None and total_qty < item["borrowed_qty"]:
            raise ValueError(
                f"Total quantity ({total_qty}) cannot be less than borrowed quantity ({item['borrowed_qty']})",
            )

        updates.append("total_qty = :total_qty")
        values["total_qty"] = total_qty

    if borrowed_qty is not None:
        if borrowed_qty < 0:
            raise ValueError("Borrowed quantity cannot be negative")

        # Check if borrowed_qty would exceed total_qty
        check_total = total_qty if total_qty is not None else item["total_qty"]
        if borrowed_qty > check_total:
            raise ValueError(
                f"Borrowed quantity ({borrowed_qty}) cannot exceed total quantity ({check_total})",
            )

        updates.append("borrowed_qty = :borrowed_qty")
        values["borrowed_qty"] = borrowed_qty

    # If no fields to update, return the current item
    if not updates:
        return item

    # Update the item
    # ruff: noqa: S608
    query = f"""
        UPDATE items
        SET {', '.join(updates)}
        WHERE id = :id
    """

    await database.execute(query, values=values)

    # Return the updated item
    return await get_item(id)


async def delete_item(id: int):
    # First check if the item exists
    item = await get_item(id)
    if not item:
        return False

    # Delete the item
    query = """
        DELETE FROM items
        WHERE id = :id
    """
    await database.execute(query, values={"id": id})

    return True


async def borrow_item(
    item_id: int,
    borrower_name: str,
    borrower_section: str,
    amount: int,
):
    # Check if the item exists and has enough available quantity
    item = await get_item(item_id)
    if not item:
        raise ValueError(f"Item with ID {item_id} does not exist")

    available_qty = item["total_qty"] - item["borrowed_qty"]

    if amount <= 0:
        raise ValueError("Borrowed amount must be greater than zero")

    if amount > available_qty:
        raise ValueError(
            f"Not enough available quantity. Requested: {amount}, Available: {available_qty}",
        )

    # Transaction to ensure data consistency
    async with database.transaction():
        # Get or create borrower
        borrower_query = """
            SELECT id FROM borrowers
            WHERE name = :name AND section = :section
        """
        borrower = await database.fetch_one(
            borrower_query,
            values={"name": borrower_name, "section": borrower_section},
        )

        if borrower:
            borrower_id = borrower["id"]
        else:
            # Create a new borrower
            insert_borrower_query = """
                INSERT INTO borrowers (name, section)
                VALUES (:name, :section)
                RETURNING id
            """
            borrower_id = await database.execute(
                insert_borrower_query,
                values={"name": borrower_name, "section": borrower_section},
            )

        # Update item's borrowed quantity
        update_item_query = """
            UPDATE items
            SET borrowed_qty = borrowed_qty + :amount
            WHERE id = :item_id
        """
        await database.execute(
            update_item_query,
            values={"item_id": item_id, "amount": amount},
        )

        # Create borrow record
        insert_borrow_query = """
            INSERT INTO borrows (item_id, borrower_id, amount, borrowed_at)
            VALUES (:item_id, :borrower_id, :amount, :borrowed_at)
            RETURNING id
        """
        borrow_id = await database.execute(
            insert_borrow_query,
            values={
                "item_id": item_id,
                "borrower_id": borrower_id,
                "amount": amount,
                "borrowed_at": datetime.now(UTC),
            },
        )

    # Return borrow transaction details
    result_query = """
        SELECT
            b.id AS borrow_id,
            b.amount,
            b.borrowed_at,
            i.id AS item_id,
            i.name AS item_name,
            br.id AS borrower_id,
            br.name AS borrower_name,
            br.section AS borrower_section
        FROM borrows b
        JOIN items i ON b.item_id = i.id
        JOIN borrowers br ON b.borrower_id = br.id
        WHERE b.id = :borrow_id
    """

    return await database.fetch_one(result_query, values={"borrow_id": borrow_id})


async def return_item(item_id: int, borrower_id: int):
    # Find all unreturned borrows for this item and borrower
    find_borrows_query = """
        SELECT id, amount
        FROM borrows
        WHERE item_id = :item_id
          AND borrower_id = :borrower_id
          AND returned_at IS NULL
    """

    borrows = await database.fetch_all(
        find_borrows_query,
        values={"item_id": item_id, "borrower_id": borrower_id},
    )

    if not borrows:
        raise ValueError(
            f"No unreturned borrows found for item_id={item_id} and borrower_id={borrower_id}",
        )

    total_returned = sum(borrow["amount"] for borrow in borrows)
    borrow_ids = [borrow["id"] for borrow in borrows]

    # Transaction to ensure data consistency
    async with database.transaction():
        # Update borrows to mark as returned
        update_borrows_query = """
            UPDATE borrows
            SET returned_at = :returned_at
            WHERE id IN ({})
        """.format(",".join(f":{i}" for i in range(len(borrow_ids))))

        values = {"returned_at": datetime.now(UTC)}
        for i, borrow_id in enumerate(borrow_ids):
            values[str(i)] = borrow_id

        await database.execute(update_borrows_query, values=values)

        # Update item's borrowed quantity
        update_item_query = """
            UPDATE items
            SET borrowed_qty = borrowed_qty - :amount
            WHERE id = :item_id
        """
        await database.execute(
            update_item_query,
            values={"item_id": item_id, "amount": total_returned},
        )

    # Return updated borrow records
    get_updated_borrows_query = """
        SELECT
            b.id AS borrow_id,
            b.amount,
            b.borrowed_at,
            b.returned_at,
            i.id AS item_id,
            i.name AS item_name,
            br.id AS borrower_id,
            br.name AS borrower_name,
            br.section AS borrower_section
        FROM borrows b
        JOIN items i ON b.item_id = i.id
        JOIN borrowers br ON b.borrower_id = br.id
        WHERE b.id IN ({})
    """.format(",".join(f":{i}" for i in range(len(borrow_ids))))

    values = {}
    for i, borrow_id in enumerate(borrow_ids):
        values[str(i)] = borrow_id

    return await database.fetch_all(get_updated_borrows_query, values=values)
