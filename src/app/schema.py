import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class HealthCheck(BaseModel):
    name: str
    version: str
    description: str


class UUIDSchema(BaseModel):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4)
