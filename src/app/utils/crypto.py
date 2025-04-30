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