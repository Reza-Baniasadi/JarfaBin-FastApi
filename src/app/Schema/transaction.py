from pydantic import BaseModel
from datetime import datetime

class TransactionBase(BaseModel):
    sender: str
    receiver: str
    amount: float
    timestamp: datetime

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    transaction_id: int

    class Config:
        orm_mode = True
