from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class LoginFormData(BaseModel):
    username: str
    password: str


LoginForm = Annotated[LoginFormData, Form()]
