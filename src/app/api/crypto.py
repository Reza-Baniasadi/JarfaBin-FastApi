from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from . import crud, schemas, tasks

router = APIRouter(prefix="/crypto", tags=["Crypto"])

@router.post("/", response_model=schemas.CryptoCurrency)
def create_crypto(crypto: schemas.CryptoCurrencyCreate, db: Session = Depends(get_db)):
    db_crypto = crud.get_crypto_by_symbol(db, crypto.symbol)
    if db_crypto:
        raise HTTPException(status_code=400, detail="Crypto already exists")
    return crud.create_crypto(db, crypto)

@router.get("/", response_model=List[schemas.CryptoCurrency])
def list_cryptos(db: Session = Depends(get_db)):
    return db.query(crud.models.CryptoCurrency).all()


@router.post("/user", response_model=schemas.UserCrypto)
def add_user_crypto(user_crypto: schemas.UserCryptoCreate, db: Session = Depends(get_db), user_id: int = 1):
    return crud.add_user_crypto(db, user_crypto, user_id)