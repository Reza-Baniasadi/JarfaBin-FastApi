from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from utils.file_utils import read_any, clean_crypto_df, to_parquet_bytes
import json
import httpx

app = FastAPI(title="Crypto Data Processor API", version="0.2.0")


class CleaningOptions(BaseModel):
    resample_interval: Optional[str] = Field(None, description="مثلاً '1min', '5min', '1H', '1D'")
    pair_separator: Optional[str] = Field('/', description="جداکننده جفت ارز")
    fill_method: Literal['ffill','bfill','none'] = 'ffill'
    ticker_mapping: Optional[Dict[str, str]] = None


@app.post("/process/clean")
async def clean_uploaded_file(
    uploaded_file: UploadFile = File(...),
    resample_interval: Optional[str] = Form(None),
    pair_separator: Optional[str] = Form('/'),
    fill_method: str = Form('ffill'),
    ticker_map_json: Optional[str] = Form(None),
):
    raw_content = await uploaded_file.read()
    df = read_any(raw_content, uploaded_file.filename)
    ticker_map = json.loads(ticker_map_json) if ticker_map_json else None

    cleaned_df, summary = clean_crypto_df(
        df,
        symbol_map=ticker_map,
        base_quote_sep=pair_separator or None,
        resample_to=resample_interval,
        freq_fill=fill_method,
    )

    preview_data = cleaned_df.head(10).to_dict(orient="records")

    return JSONResponse({"summary": summary.__dict__, "preview": preview_data})


@app.post("/process/clean/parquet")
async def clean_and_export_parquet(
    uploaded_file: UploadFile = File(...),
    resample_interval: Optional[str] = Form(None),
    pair_separator: Optional[str] = Form('/'),
    fill_method: str = Form('ffill'),
    ticker_map_json: Optional[str] = Form(None),
):
    raw_content = await uploaded_file.read()
    df = read_any(raw_content, uploaded_file.filename)
    ticker_map = json.loads(ticker_map_json) if ticker_map_json else None

    cleaned_df, _ = clean_crypto_df(
        df,
        symbol_map=ticker_map,
        base_quote_sep=pair_separator or None,
        resample_to=resample_interval,
        freq_fill=fill_method,
    )

    parquet_bytes = to_parquet_bytes(cleaned_df)

    return JSONResponse({"size_bytes": len(parquet_bytes)})


class TickerMappingBody(BaseModel):
    mapping: Dict[str, str] = Field(..., description="{'XBTUSDT': 'BTCUSDT', 'ETH-USD': 'ETHUSD'}")


@app.post("/symbols/normalize")
async def normalize_ticker_symbols(file: UploadFile = File(...), body: TickerMappingBody = None):
    from utils.file_utils import standardize_columns, normalize_tickers

    raw_content = await file.read()
    df = read_any(raw_content, file.filename)
    df = standardize_columns(df)
    df = normalize_tickers(df, mapping=(body.mapping if body else None), base_quote_sep='/')
    return {"preview": df.head(10).to_dict(orient="records")}


@app.get("/system/health")
async def check_health():
    return {"status": "healthy"}


@app.post("/model/analyze", response_model=schemas.ModelResponse)
async def model_analysis(request_data: schemas.ModelRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(settings.MODEL_ENDPOINT, json=request_data.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Model error: {response.text}")
        result = response.json()
        return schemas.ModelResponse(predictions=result.get("predictions"), raw=result)


@app.post("/crypto/{ticker}", response_model=schemas.CryptoPriceResponse)
async def add_crypto_price(ticker: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = await fetch_price(ticker)
    usd_price = float(data.get("price_usd") or data.get("price") or 0)
    toman_price = usd_price * float(data.get("tether_rate", 0)) if data.get("tether_rate") else None

    background_tasks.add_task(store_price_task, ticker.upper(), usd_price, toman_price, db)


def store_price_task(ticker: str, usd: float, toman: Optional[float], db: Session):
    from schemas import CryptoPriceCreate
    import crud

    price_record = CryptoPriceCreate(symbol=ticker, price_usd=usd, price_toman=toman)
    crud.create_price(db, price_record)

    return schemas.CryptoPriceResponse(
        id=0,
        symbol=ticker.upper(),
        price_usd=usd,
        price_toman=toman,
        timestamp=None
    )
