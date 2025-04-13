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


@router.post("/update-prices")
async def update_prices(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(tasks.update_all_crypto_prices, db)
    return {"message": "Price update started in background"}


@app.post("/model/predict", response_model=ModelResponse)
async def predict_with_model(req: ModelRequest):
    payload = req.dict(exclude_none=True)
    model_resp = await call_model_endpoint(payload)
    return ModelResponse(predictions=model_resp.get("predictions"), raw=model_resp)


@app.get("/check-config")
async def check_config():
    return {
        "ARZDIGITAL_API_KEY": settings.ARZDIGITAL_API_KEY,
        "MODEL_ENDPOINT": settings.MODEL_ENDPOINT,
        "MODEL_API_KEY": settings.MODEL_API_KEY
    }