from sqlalchemy.orm import Session
from . import models, schemas

def get_crypto(db: Session, crypto_id: int):
    return db.query(models.CryptoCurrency).filter(models.CryptoCurrency.id == crypto_id).first()


def get_crypto_by_symbol(db: Session, symbol: str):
    return db.query(models.CryptoCurrency).filter(models.CryptoCurrency.symbol == symbol).first()


def create_crypto(db: Session, crypto: schemas.CryptoCurrencyCreate):
    db_crypto = models.CryptoCurrency(name=crypto.name, symbol=crypto.symbol, price_usd=0)
    db.add(db_crypto)
    db.commit()
    db.refresh(db_crypto)
    return db_crypto

def update_crypto_price(db: Session, crypto_id: int, price_usd: float):
    crypto = get_crypto(db, crypto_id)
    if crypto:
        crypto.price_usd = price_usd
        db.commit()
        db.refresh(crypto)
    return crypto