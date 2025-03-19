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
    qty: int
