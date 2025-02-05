from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(256), nullable=False)
    amount = Column(String, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'income' or 'expense'
    category = Column(String(50), nullable=False)  # Example: 'salary', 'groceries'
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
