from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.schemas import TimestampSchema


def sanitize_path(path: str) -> str:
    return path.strip("/").replace("/", "_")