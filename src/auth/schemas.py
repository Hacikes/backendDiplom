from typing import Optional

from pydantic import BaseModel

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = True
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = True
    is_verified: Optional[bool] = False

class UserUpdate(schemas.BaseUserUpdate):
    username: str
    email: Optional[str]
    password: Optional[str]
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = True
    is_verified: Optional[bool] = False

class ForgotPassword(BaseModel):
    email: str