import json
from pydantic import BaseModel,RootModel, ValidationError
from datetime import datetime, date, datetime
from typing import Optional
from uuid import UUID as UUID_4


class Login(BaseModel):
    id: UUID_4
    password: str


class UserInfo(BaseModel):
    id: UUID_4
    first_name: str
    second_name: str
    birthdate: date
    biography: str
    city: str


class UserInfoList(RootModel):
    root: list[UserInfo]


class User(UserInfo):
    password: str


class AuthInfo(BaseModel):
    id: UUID_4
    password: str
    token: str
    token_create_dt: datetime
    token_valid_dt: datetime
