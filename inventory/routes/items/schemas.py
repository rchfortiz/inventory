from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class EditItemFormData(BaseModel):
    name: str
    description: str
    location: str


class BorrowItemFormData(BaseModel):
    borrower_id: int
    quantity: int


class AddItemFormData(BaseModel):
    name: str
    description: str
    location: str
    quantity: int


EditItemForm = Annotated[EditItemFormData, Form()]
BorrowItemForm = Annotated[BorrowItemFormData, Form()]
AddItemForm = Annotated[AddItemFormData, Form()]
