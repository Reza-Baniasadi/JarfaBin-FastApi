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