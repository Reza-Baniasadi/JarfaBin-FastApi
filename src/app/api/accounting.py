from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from accounting_models import Transaction
from accounting_schemas import TransactionCreate, TransactionOut
from accounting_database import get_db

router = APIRouter()

@router.post("/", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(**payload.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/category/{category}", response_model=list[TransactionOut])
def get_transactions_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.category == category).all()

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return None