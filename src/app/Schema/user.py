from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, example="User Userson")]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", example="userson")]
    email: Annotated[EmailStr, Field(example="user.userson@example.com")]


class UserCreate(UserBase):
    password: Annotated[
        str,
        Field(
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            example="Str1ngst!"
        )
    ]
    model_config = ConfigDict(extra="forbid")


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=2, max_length=30, example="User Userberg", default=None)]
    username: Annotated[str | None, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", example="userberg", default=None)]
    email: Annotated[EmailStr | None, Field(example="user.userberg@example.com", default=None)]
    profile_image_url: Annotated[HttpUrl | None, Field(default=None, example="https://www.profileimageurl.com")]
    model_config = ConfigDict(extra="forbid")


class UserUpdateInternal(UserUpdate, TimestampSchema):
    updated_at: datetime


class UserRead(UserBase, UUIDSchema, TimestampSchema):
    id: int
    profile_image_url: HttpUrl
    tier_id: int | None


class UserTierUpdate(BaseModel):
    tier_id: int


class UserDelete(PersistentDeletion):
    model_config = ConfigDict(extra="forbid")


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
