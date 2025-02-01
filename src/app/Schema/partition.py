from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PartitionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PartitionCreate(PartitionBase):
    pass

class PartitionOut(PartitionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    size_bytes: int
    record_count: int

class PartitionUpdate(BaseModel):
    description: Optional[str] = None
    size_bytes: Optional[int] = None
    record_count: Optional[int] = None