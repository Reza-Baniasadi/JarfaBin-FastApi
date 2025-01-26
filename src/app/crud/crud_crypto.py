from sqlalchemy.orm import Session
from . import models, schemas

def get_crypto(db: Session, crypto_id: int):
    return db.query(models.CryptoCurrency).filter(models.CryptoCurrency.id == crypto_id).first()