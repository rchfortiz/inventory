import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NotRequired, TypedDict

INIT_SCRIPT = Path("sql/init.sql")


class AssetData(TypedDict):
    asset_name: str
    category_id: int
    brand: NotRequired[str | None]
    model_number: NotRequired[str | None]
    serial_number: NotRequired[str | None]
    purchase_date: NotRequired[str | None]
    purchase_price: NotRequired[float | None]
    condition: NotRequired[str]
    location_id: NotRequired[int | None]
    assigned_to: NotRequired[int | None]
    notes: NotRequired[str | None]


class UserData(TypedDict):
    name: str
    department: NotRequired[str | None]
    role: NotRequired[str]
    contact_info: NotRequired[str | None]


class AssetFilters(TypedDict, total=False):
    category_id: int
    condition: str
    location_id: int


ReportType = str  # 'by_category' | 'by_condition' | 'check_out_history'
DBRow = dict[str, Any]


class Database:
    def __init__(self, db_path: str = "inventory.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(INIT_SCRIPT.read_text())

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.conn.close()

    def add_asset(self, asset_data: AssetData) -> int:
        """Add a new asset to the database."""
        query = """
            INSERT INTO assets (
                asset_name, category_id, brand, model_number,
                serial_number, purchase_date, purchase_price, condition,
                location_id, assigned_to, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.execute(
            query,
            (
                asset_data["asset_name"],
                asset_data["category_id"],
                asset_data.get("brand"),
                asset_data.get("model_number"),
                asset_data.get("serial_number"),
                asset_data.get("purchase_date"),
                asset_data.get("purchase_price"),
                asset_data.get("condition", "New"),
                asset_data.get("location_id"),
                asset_data.get("assigned_to"),
                asset_data.get("notes"),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid or 0

    def get_asset(self, asset_id: int) -> DBRow | None:
        """Retrieve an asset by ID."""
        query = """
            SELECT a.*, c.name as category_name,
                   l.building, l.room_number,
                   u.name as assigned_to_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.category_id
            LEFT JOIN locations l ON a.location_id = l.location_id
            LEFT JOIN users u ON a.assigned_to = u.user_id
            WHERE a.asset_id = ?
        """
        cursor = self.conn.execute(query, (asset_id,))
        result = cursor.fetchone()
        return dict(result) if result else None

    def update_asset(self, asset_id: int, asset_data: AssetData) -> bool:
        """Update an existing asset."""
        current_asset = self.get_asset(asset_id)
        if not current_asset:
            return False

        update_fields: list[str] = []
        values: list[Any] = []
        for key, value in asset_data.items():
            if key in current_asset and value is not None:
                update_fields.append(f"{key} = ?")
                values.append(value)

        if not update_fields:
            return False

        query = f"UPDATE assets SET {', '.join(update_fields)} WHERE asset_id = ?"  # noqa: S608
        values.append(asset_id)

        self.conn.execute(query, values)
        self.conn.commit()
        return True

    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset from the database."""
        cursor = self.conn.execute("DELETE FROM assets WHERE asset_id = ?", (asset_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def search_assets(self, filters: AssetFilters | None = None) -> Sequence[DBRow]:
        """Search assets with optional filters."""
        query = """
            SELECT a.*, c.name as category_name,
                   l.building, l.room_number,
                   u.name as assigned_to_name
            FROM assets a
            LEFT JOIN categories c ON a.category_id = c.category_id
            LEFT JOIN locations l ON a.location_id = l.location_id
            LEFT JOIN users u ON a.assigned_to = u.user_id
            WHERE 1=1
        """
        params: list[Any] = []
        if filters:
            if "category_id" in filters:
                query += " AND a.category_id = ?"
                params.append(filters["category_id"])
            if "condition" in filters:
                query += " AND a.condition = ?"
                params.append(filters["condition"])
            if "location_id" in filters:
                query += " AND a.location_id = ?"
                params.append(filters["location_id"])

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def check_out_asset(
        self,
        asset_id: int,
        user_id: int,
        expected_return_date: str,
        notes: str | None = None,
    ) -> bool:
        """Check out an asset to a user."""
        try:
            self.conn.execute(
                """
                INSERT INTO asset_transactions (
                    asset_id, user_id, transaction_type,
                    checkout_date, expected_return_date, notes
                ) VALUES (?, ?, 'check_out', datetime('now'), ?, ?)
            """,
                (asset_id, user_id, expected_return_date, notes),
            )

            self.conn.execute(
                """
                UPDATE assets
                SET assigned_to = ?
                WHERE asset_id = ?
            """,
                (user_id, asset_id),
            )

            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def check_in_asset(
        self,
        asset_id: int,
        condition: str,
        notes: str | None = None,
    ) -> bool:
        """Check in an asset."""
        try:
            self.conn.execute(
                """
                INSERT INTO asset_transactions (
                    asset_id, user_id, transaction_type,
                    actual_return_date, condition_on_return, notes
                )
                SELECT ?, assigned_to, 'check_in', datetime('now'), ?, ?
                FROM assets WHERE asset_id = ?
            """,
                (asset_id, condition, notes, asset_id),
            )

            self.conn.execute(
                """
                UPDATE assets
                SET assigned_to = NULL,
                    condition = ?
                WHERE asset_id = ?
            """,
                (condition, asset_id),
            )

            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def add_user(self, user_data: UserData) -> int:
        """Add a new user."""
        query = """
            INSERT INTO users (name, department, role, contact_info)
            VALUES (?, ?, ?, ?)
        """
        cursor = self.conn.execute(
            query,
            (
                user_data["name"],
                user_data.get("department"),
                user_data.get("role", "Staff"),
                user_data.get("contact_info"),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid or 0

    def get_user(self, user_id: int) -> DBRow | None:
        """Retrieve a user by ID."""
        cursor = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None

    def generate_asset_report(self, report_type: ReportType) -> Sequence[DBRow]:
        """Generate various asset reports."""
        queries: dict[str, str] = {
            "by_category": """
                SELECT c.name as category, COUNT(*) as count
                FROM assets a
                JOIN categories c ON a.category_id = c.category_id
                GROUP BY c.category_id, c.name
            """,
            "by_condition": """
                SELECT condition, COUNT(*) as count
                FROM assets
                GROUP BY condition
            """,
            "check_out_history": """
                SELECT at.*, a.asset_name, u.name as user_name
                FROM asset_transactions at
                JOIN assets a ON at.asset_id = a.asset_id
                JOIN users u ON at.user_id = u.user_id
                ORDER BY at.created_at DESC
            """,
        }

        if report_type not in queries:
            msg = f"Unknown report type: {report_type}"
            raise ValueError(msg)

        cursor = self.conn.execute(queries[report_type])
        return [dict(row) for row in cursor.fetchall()]

    def get_setting(self, setting_name: str) -> str | None:
        """Retrieve a setting value."""
        cursor = self.conn.execute(
            "SELECT setting_value FROM settings WHERE setting_name = ?",
            (setting_name,),
        )
        result = cursor.fetchone()
        return dict(result)["setting_value"] if result else None

    def update_setting(self, setting_name: str, setting_value: str) -> bool:
        """Update a setting value."""
        cursor = self.conn.execute(
            """
            UPDATE settings
            SET setting_value = ?
            WHERE setting_name = ?
        """,
            (setting_value, setting_name),
        )
        self.conn.commit()
        return cursor.rowcount > 0
