from datetime import datetime
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
    due_date: datetime


class AddItemFormData(BaseModel):
    name: str
    description: str
    category: str
    location: str
    quantity: int


EditItemForm = Annotated[EditItemFormData, Form()]
BorrowItemForm = Annotated[BorrowItemFormData, Form()]
AddItemForm = Annotated[AddItemFormData, Form()]
