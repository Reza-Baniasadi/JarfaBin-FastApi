import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class HealthCheck(BaseModel):
    name: str
    version: str
    description: str
