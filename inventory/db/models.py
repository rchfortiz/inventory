from datetime import UTC, datetime
from enum import IntEnum

from sqlmodel import Field, Relationship, SQLModel


class Role(IntEnum):
    STAFF = 0
    ADMIN = 1


class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password_hash: bytes
    role: Role


class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    category: str
    location: str
    total_qty: int
    borrows: list["Borrow"] = Relationship(back_populates="item")

    @property
    def available_qty(self) -> int:
        borrowed_qty = sum(borrow.qty for borrow in self.borrows) if self.borrows else 0
        return self.total_qty - borrowed_qty


class Borrower(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    section: str
    borrows: list["Borrow"] = Relationship(back_populates="borrower")


class Borrow(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    borrower_id: int = Field(foreign_key="borrower.id")
    item: Item = Relationship(back_populates="borrows")
    borrower: Borrower = Relationship(back_populates="borrows")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    due_date: datetime
    qty: int

    @property
    def is_overdue(self) -> bool:
        return self.created_at > self.due_date

    @property
    def due_date_str(self) -> str:
        return self.due_date.strftime("%b %e %Y")


class Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="user.username")
    action: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def created_at_str(self) -> str:
        return self.created_at.strftime("%b %e %Y, %l:%S %p")
