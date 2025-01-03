from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class PostBase(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    text: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]