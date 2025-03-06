from collections.abc import AsyncGenerator

import pytest
from databases import Database
from httpx import ASGITransport, AsyncClient

from inventory import app
from inventory.database import get_db, run_init_script
from inventory.services.user import User, get_user_dep

TEST_USERNAME = "testuser"
TEST_ROLE = "admin"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def test_db() -> AsyncGenerator[Database]:
    db = Database("sqlite+aiosqlite:///:memory:", force_rollback=True)
    await db.connect()
    await run_init_script(db)
    yield db
    await db.disconnect()


@pytest.fixture
async def client(test_db: Database) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_user_dep] = lambda: User(TEST_USERNAME, b"", TEST_ROLE)

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
