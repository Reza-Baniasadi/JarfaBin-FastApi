from sqlalchemy.orm import Session
from . import models, schemas
from typing import List


def fetch_crypto(db: Session, crypto_id: int) -> models.CryptoCurrency | None:
    """Retrieve a cryptocurrency by its ID."""
    return db.query(models.CryptoCurrency).filter(models.CryptoCurrency.id == crypto_id).first()


def fetch_crypto_by_symbol(db: Session, symbol: str) -> models.CryptoCurrency | None:
    """Retrieve a cryptocurrency by its symbol."""
    return db.query(models.CryptoCurrency).filter(models.CryptoCurrency.symbol == symbol).first()


def add_crypto(db: Session, crypto_data: schemas.CryptoCurrencyCreate) -> models.CryptoCurrency:
    """Create a new cryptocurrency with initial USD price of 0."""
    new_crypto = models.CryptoCurrency(name=crypto_data.name, symbol=crypto_data.symbol, price_usd=0)
    db.add(new_crypto)
    db.commit()
    db.refresh(new_crypto)
    return new_crypto


def set_crypto_price(db: Session, crypto_id: int, price_usd: float) -> models.CryptoCurrency | None:
    """Update the USD price of a cryptocurrency."""
    crypto = fetch_crypto(db, crypto_id)
    if crypto:
        crypto.price_usd = price_usd
        db.commit()
        db.refresh(crypto)
    return crypto


def add_user_crypto_entry(db: Session, user_crypto_data: schemas.UserCryptoCreate, user_id: int) -> models.UserCrypto:
    """Add a cryptocurrency entry for a specific user."""
    user_crypto = models.UserCrypto(
        user_id=user_id,
        crypto_id=user_crypto_data.crypto_id,
        amount=user_crypto_data.amount,
    )
    db.add(user_crypto)
    db.commit()
    db.refresh(user_crypto)
    return user_crypto


def fetch_user_cryptos(db: Session, user_id: int) -> List[models.UserCrypto]:
    """Get all cryptocurrency entries for a specific user."""
    return db.query(models.UserCrypto).filter(models.UserCrypto.user_id == user_id).all()
