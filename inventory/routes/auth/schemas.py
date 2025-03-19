from typing import Annotated

from fastapi import Form
from pydantic import BaseModel

from inventory.db.models import Role


class LoginFormData(BaseModel):
    username: str
    password: str


class RegisterFormData(BaseModel):
    username: str
    password: str
    role: Role


LoginForm = Annotated[LoginFormData, Form()]
RegisterForm = Annotated[RegisterFormData, Form()]
