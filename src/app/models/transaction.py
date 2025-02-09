from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    receiver = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime)
