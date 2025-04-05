from typing import Annotated

from fastapi import Form
from pydantic import BaseModel

from inventory.db.models import Role


class NewUserFormData(BaseModel):
    username: str
    password: str
    role: Role


NewUserForm = Annotated[NewUserFormData, Form()]
