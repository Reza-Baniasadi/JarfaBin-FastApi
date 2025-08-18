from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from typing import List, Optional


def add_transaction(db: Session, transaction_data: schemas.TransactionCreate) -> models.Transaction:
    """Insert a new transaction record into the database."""
    new_transaction = models.Transaction(
        sender=transaction_data.sender,
        receiver=transaction_data.receiver,
        amount=transaction_data.amount,
        timestamp=transaction_data.timestamp
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


def fetch_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Transaction]:
    """Retrieve a list of transactions with pagination support."""
    return db.query(models.Transaction).offset(skip).limit(limit).all()


def fetch_transaction_by_id(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    """Retrieve a single transaction by its unique ID."""
    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
