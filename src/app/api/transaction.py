from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas as s, crud as c, database as db_mod

finance_router = APIRouter(prefix="/finance", tags=["transactions"])

async def _get_db_session() -> Session:
    return db_mod.get_db()

@finance_router.post("/add", response_model=s.TransactionResponse)
async def add_transaction(tx_data: s.TransactionCreate, db: Session = Depends(_get_db_session)):
    return c.create_transaction(db=db, transaction=tx_data)

@finance_router.get("/list", response_model=list[s.TransactionResponse])
async def list_transactions(start: int = 0, count: int = 100, db: Session = Depends(_get_db_session)):
    return c.get_transactions(db=db, skip=start, limit=count)

@finance_router.get("/detail/{tx_id}", response_model=s.TransactionResponse)
async def transaction_detail(tx_id: int, db: Session = Depends(_get_db_session)):
    return c.get_transaction(db=db, transaction_id=tx_id)
