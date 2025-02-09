from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        sender=transaction.sender,
        receiver=transaction.receiver,
        amount=transaction.amount,
        timestamp=transaction.timestamp
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
