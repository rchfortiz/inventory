from databases import Database

from inventory.settings import settings

database = Database(settings.database_url)


async def prepare_tables():
    await database.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            total_qty    INTEGER NOT NULL CHECK (total_qty >= 0),
            borrowed_qty INTEGER NOT NULL DEFAULT 0 CHECK (borrowed_qty >= 0)
        )
    """)

    await database.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    await database.execute("""
        CREATE TABLE IF NOT EXISTS borrows (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id     INTEGER NOT NULL,
            borrower_id INTEGER NOT NULL,
            amount      INTEGER NOT NULL,
            borrowed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            returned_at TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(id) ON DELETE CASCADE,
            CHECK (returned_at IS NULL OR returned_at >= borrowed_at)
        )
    """)
