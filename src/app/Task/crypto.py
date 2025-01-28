from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from . import crud, models, services

async def update_all_crypto_prices(db: Session):
    cryptos = db.query(models.CryptoCurrency).all()
    for crypto in cryptos:
        price = await services.fetch_crypto_price(crypto.symbol)
        crud.update_crypto_price(db, crypto.id, price)
