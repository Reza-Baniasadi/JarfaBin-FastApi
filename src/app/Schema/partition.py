from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PartitionBase(BaseModel):
    name: str
    description: Optional[str] = None