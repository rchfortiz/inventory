from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class AddBorrowerFormData(BaseModel):
    name: str


AddBorrowerForm = Annotated[AddBorrowerFormData, Form()]
