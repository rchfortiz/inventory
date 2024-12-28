from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from inventory.database import (
    AssetData,
    AssetFilters,
    Database,
    DBRow,
    UserData,
)


@pytest.fixture
def db() -> Generator[Database]:
    """Create a temporary database for testing."""
    db_path: str = "test_inventory.db"
    db = Database(db_path)
    yield db
    db.conn.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_user_data() -> UserData:
    return {
        "name": "John Doe",
        "department": "IT",
        "role": "Staff",
        "contact_info": "john@example.com",
    }


@pytest.fixture
def sample_asset_data() -> AssetData:
    return {
        "asset_name": "Test Laptop",
        "category_id": 1,  # Computer category
        "brand": "TestBrand",
        "model_number": "TB123",
        "serial_number": "SN123456",
        "purchase_date": "2024-01-01",
        "purchase_price": 999.99,
        "condition": "New",
        "notes": "Test asset",
    }


def test_add_asset(db: Database, sample_asset_data: AssetData) -> None:
    """Test adding a new asset."""
    asset_id: int = db.add_asset(sample_asset_data)
    assert asset_id > 0

    # Verify the asset was added correctly
    asset: DBRow | None = db.get_asset(asset_id)
    assert asset is not None
    assert asset["asset_name"] == sample_asset_data["asset_name"]
    assert asset["brand"] == sample_asset_data.get("brand")
    assert asset["category_name"] == "Computer"


def test_update_asset(db: Database, sample_asset_data: AssetData) -> None:
    """Test updating an existing asset."""
    asset_id: int = db.add_asset(sample_asset_data)

    # Update asset data
    updated_data: AssetData = {
        "asset_name": "Updated Laptop",
        "category_id": 1,
        "condition": "Good",
    }

    success: bool = db.update_asset(asset_id, updated_data)
    assert success is True

    # Verify the update
    asset: DBRow | None = db.get_asset(asset_id)
    assert asset is not None
    assert asset["asset_name"] == "Updated Laptop"
    assert asset["condition"] == "Good"
    assert asset["brand"] == sample_asset_data.get("brand")  # Unchanged field


def test_delete_asset(db: Database, sample_asset_data: AssetData) -> None:
    """Test deleting an asset."""
    asset_id: int = db.add_asset(sample_asset_data)

    success: bool = db.delete_asset(asset_id)
    assert success is True

    # Verify the asset was deleted
    asset: DBRow | None = db.get_asset(asset_id)
    assert asset is None


def test_search_assets(db: Database, sample_asset_data: AssetData) -> None:
    """Test searching assets with filters."""
    db.add_asset(sample_asset_data)

    # Test searching by category
    filters: AssetFilters = {"category_id": 1}
    results = db.search_assets(filters)
    assert len(results) > 0
    assert all(r["category_id"] == 1 for r in results)

    # Test searching by condition
    filters = {"condition": "New"}
    results = db.search_assets(filters)
    assert len(results) > 0
    assert all(r["condition"] == "New" for r in results)


def test_add_user(db: Database, sample_user_data: UserData) -> None:
    """Test adding a new user."""
    user_id: int = db.add_user(sample_user_data)
    assert user_id > 0

    # Verify the user was added
    user: DBRow | None = db.get_user(user_id)
    assert user is not None
    assert user["name"] == sample_user_data["name"]
    assert user["department"] == sample_user_data.get("department")


def test_check_out_asset(
    db: Database,
    sample_asset_data: AssetData,
    sample_user_data: UserData,
) -> None:
    """Test checking out an asset to a user."""
    asset_id: int = db.add_asset(sample_asset_data)
    user_id: int = db.add_user(sample_user_data)

    expected_return_date: str = (datetime.now(tz=UTC) + timedelta(days=14)).strftime("%Y-%m-%d")

    success: bool = db.check_out_asset(
        asset_id=asset_id,
        user_id=user_id,
        expected_return_date=expected_return_date,
        notes="Test checkout",
    )
    assert success is True

    # Verify the checkout
    asset: DBRow | None = db.get_asset(asset_id)
    assert asset is not None
    assert asset["assigned_to"] == user_id

    # Check transaction history
    report = db.generate_asset_report("check_out_history")
    assert len(report) > 0
    assert report[0]["asset_id"] == asset_id
    assert report[0]["user_id"] == user_id
    assert report[0]["transaction_type"] == "check_out"


def test_check_in_asset(
    db: Database,
    sample_asset_data: AssetData,
    sample_user_data: UserData,
) -> None:
    """Test checking in an asset."""
    asset_id: int = db.add_asset(sample_asset_data)
    user_id: int = db.add_user(sample_user_data)

    # First check out the asset
    expected_return_date: str = (datetime.now(tz=UTC) + timedelta(days=14)).strftime("%Y-%m-%d")
    db.check_out_asset(asset_id, user_id, expected_return_date)

    # Now check it back in
    success: bool = db.check_in_asset(
        asset_id=asset_id,
        condition="Good",
        notes="Test check-in",
    )
    assert success is True

    # Verify the check-in
    asset: DBRow | None = db.get_asset(asset_id)
    assert asset is not None
    assert asset["assigned_to"] is None
    assert asset["condition"] == "Good"


def test_generate_asset_report(db: Database, sample_asset_data: AssetData) -> None:
    """Test generating different types of asset reports."""
    db.add_asset(sample_asset_data)

    # Test category report
    category_report = db.generate_asset_report("by_category")
    assert len(category_report) > 0
    assert "category" in category_report[0]
    assert "count" in category_report[0]

    # Test condition report
    condition_report = db.generate_asset_report("by_condition")
    assert len(condition_report) > 0
    assert "condition" in condition_report[0]
    assert "count" in condition_report[0]


def test_settings(db: Database) -> None:
    """Test getting and updating settings."""
    # Test getting default setting
    loan_period: str | None = db.get_setting("default_loan_period_days")
    assert loan_period == "14"

    # Test updating setting
    success: bool = db.update_setting("default_loan_period_days", "30")
    assert success is True

    # Verify the update
    new_loan_period: str | None = db.get_setting("default_loan_period_days")
    assert new_loan_period == "30"


def test_invalid_operations(db: Database, sample_asset_data: AssetData) -> None:
    """Test handling of invalid operations."""
    # Test updating non-existent asset
    success: bool = db.update_asset(999, sample_asset_data)
    assert success is False

    # Test deleting non-existent asset
    success = db.delete_asset(999)
    assert success is False

    # Test getting non-existent asset
    asset: DBRow | None = db.get_asset(999)
    assert asset is None

    # Test updating non-existent setting
    success = db.update_setting("non_existent_setting", "value")
    assert success is False


def test_database_context_manager(sample_asset_data: AssetData) -> None:
    """Test using the database as a context manager."""
    db_path: str = "test_inventory.db"

    with Database(db_path) as db:
        asset_id: int = db.add_asset(sample_asset_data)
        assert asset_id > 0

        asset: DBRow | None = db.get_asset(asset_id)
        assert asset is not None

    # Clean up
    Path(db_path).unlink(missing_ok=True)
