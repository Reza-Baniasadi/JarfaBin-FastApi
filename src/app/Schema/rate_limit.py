from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class PostBase(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=30, example="This is my post")]
    text: Annotated[str, Field(min_length=1, max_length=63206, example="This is the content of my post.")] 


class PostCreate(PostBase):
    media_url: Annotated[HttpUrl | None, Field(default=None, example="https://www.postimageurl.com")]
    model_config = ConfigDict(extra="forbid")


class PostCreateInternal(PostCreate):
    created_by_user_id: int


class PostUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=2, max_length=30, example="This is my updated post", default=None)]
    text: Annotated[str | None, Field(min_length=1, max_length=63206, example="This is the updated content of my post.", default=None)]
    media_url: Annotated[HttpUrl | None, Field(default=None, example="https://www.postimageurl.com")]
    model_config = ConfigDict(extra="forbid")


class PostUpdateInternal(PostUpdate, TimestampSchema):
    updated_at: datetime


class PostRead(PostBase, UUIDSchema, TimestampSchema):
    media_url: Annotated[HttpUrl | None, Field(default=None, example="https://www.postimageurl.com")]
    created_by_user_id: int


class PostDelete(BaseModel, PersistentDeletion):
    model_config = ConfigDict(extra="forbid")
