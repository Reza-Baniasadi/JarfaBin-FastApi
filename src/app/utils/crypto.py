from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from utils.file_utils import read_any, clean_crypto_df, to_parquet_bytes 
import json


app = FastAPI(title="Crypto File Utils API", version="0.1.0")


class CleanOptions(BaseModel):
    resample_to: Optional[str] = Field(None, description="مثلاً '1min', '5min', '1H', '1D'")
    base_quote_sep: Optional[str] = Field('/', description="جداکننده جفت‌ارز مثل '/' یا '-' ")
    freq_fill: Literal['ffill','bfill','none'] = 'ffill'
    symbol_map: Optional[Dict[str,str]] = None


@app.post("/files/clean")
async def clean_file(
file: UploadFile = File(...),
resample_to: Optional[str] = Form(None),
base_quote_sep: Optional[str] = Form('/'),
freq_fill: str = Form('ffill'),
symbol_map_json: Optional[str] = Form(None),
):
    raw = await file.read()
    df = read_any(raw, file.filename)
    symbol_map = json.loads(symbol_map_json) if symbol_map_json else None


    cleaned, report = clean_crypto_df(
    df,
    symbol_map=symbol_map,
    base_quote_sep=base_quote_sep or None,
    resample_to=resample_to,
    freq_fill=freq_fill,
    )
    preview = cleaned.head(10).to_dict(orient="records")
    return JSONResponse(
    content={
    "report": report.__dict__,
    "preview": preview,
    }
    )



@app.post("/files/clean/parquet")
async def clean_file_parquet(
file: UploadFile = File(...),
resample_to: Optional[str] = Form(None),
base_quote_sep: Optional[str] = Form('/'),
freq_fill: str = Form('ffill'),
symbol_map_json: Optional[str] = Form(None),
):

    raw = await file.read()
    df = read_any(raw, file.filename)
    symbol_map = json.loads(symbol_map_json) if symbol_map_json else None


    cleaned, report = clean_crypto_df(
    df,
    symbol_map=symbol_map,
    base_quote_sep=base_quote_sep or None,
    resample_to=resample_to,
    freq_fill=freq_fill,
    )
    data = to_parquet_bytes(cleaned)
    return JSONResponse(
    content={
    "bytes": len(data),
    }
    )


class SymbolMapBody(BaseModel):
    symbols: Dict[str,str] = Field(..., description="{'XBTUSDT': 'BTCUSDT', 'ETH-USD': 'ETHUSD'}")  


@app.post("/symbols/normalize")
async def normalize_symbols(file: UploadFile = File(...), body: SymbolMapBody = None):
    from utils.file_utils import read_any, standardize_columns, normalize_tickers # type: ignore
    raw = await file.read()
    df = read_any(raw, file.filename)
    df = standardize_columns(df)
    df = normalize_tickers(df, mapping=(body.symbols if body else None), base_quote_sep='/')
    return {"head": df.head(10).to_dict(orient="records")}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/model/analyze", response_model=schemas.ModelResponse)
async def analyze(req: schemas.ModelRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(settings.MODEL_ENDPOINT, json=req.dict())
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Model error: {resp.text}")
        return schemas.ModelResponse(predictions=resp.json().get("predictions"), raw=resp.json())
    

@app.post("/crypto/{symbol}", response_model=schemas.CryptoPriceResponse)
async def add_price(symbol: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = await fetch_price(symbol)
    price_usd = float(data.get("price_usd") or data.get("price") or 0)
    price_toman = price_usd * float(data.get("tether_rate", 0)) if data.get("tether_rate") else None

    background_tasks.add_task(save_price_task, symbol.upper(), price_usd, price_toman, db)

def save_price_task(symbol: str, price_usd: float, price_toman: float, db: Session):
    from schemas import CryptoPriceCreate
    import crud
    obj = CryptoPriceCreate(symbol=symbol, price_usd=price_usd, price_toman=price_toman)
    crud.create_price(db, obj)