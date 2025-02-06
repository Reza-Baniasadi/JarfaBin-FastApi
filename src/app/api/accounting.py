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