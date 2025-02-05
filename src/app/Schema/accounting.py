from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    description: str
    amount: float
    transaction_type: str  # 'income' or 'expense'
    category: str  # Example: 'salary', 'groceries'

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime
