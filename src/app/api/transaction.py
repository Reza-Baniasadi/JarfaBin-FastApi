from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, database

router = APIRouter()

@router.post("/transactions/", response_model=schemas.TransactionResponse)
async def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    return crud.create_transaction(db=db, transaction=transaction)



@router.get("/transactions/", response_model=list[schemas.TransactionResponse])
async def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_transactions(db=db, skip=skip, limit=limit)

@router.get("/transaction/{transaction_id}", response_model=schemas.TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(database.get_db)):
    return crud.get_transaction(db=db, transaction_id=transaction_id)