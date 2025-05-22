import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseSettings
import httpx
from models import CryptoPriceResponse, ModelRequest, ModelResponse
from typing import Optional


class Settings(BaseSettings):
    ARZDIGITAL_API_KEY: Optional[str] = None
    MODEL_ENDPOINT: str
    MODEL_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(title="FastAPI + ArzDigital + Model integration")

ARZ_BASE = "https://console.arzdigital.com/api"  

async def fetch_crypto_price(symbol: str) -> dict:
    headers = {}
    if settings.ARZDIGITAL_API_KEY:
        headers["Authorization"] = f"Bearer {settings.ARZDIGITAL_API_KEY}"

        params = {"symbol": symbol}
    async with httpx.AsyncClient(timeout=15.0) as client:
        # url = f"https://console.arzdigital.com/api/v1/coins/{symbol}"
        resp = await client.get(headers=headers, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"ArzDigital error: {resp.text}")
        return resp.json()

async def call_model_endpoint(payload: dict) -> dict:
    headers = {"Content-Type": "application/json"}
    if settings.MODEL_API_KEY:
        headers["Authorization"] = f"Bearer {settings.MODEL_API_KEY}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(settings.MODEL_ENDPOINT, json=payload, headers=headers)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Model error: {resp.text}")
        return resp.json()
    



@app.get("/crypto/{symbol}", response_model=CryptoPriceResponse)
async def get_crypto_price(symbol: str):
    data = await fetch_arzdigital_price(symbol)
    try:
        price_usd = float(data.get("price_usd") or data.get("price") or 0)
        price_toman = None
        if data.get("tether_rate"):
            price_toman = price_usd * float(data["tether_rate"])
        return CryptoPriceResponse(
            symbol=symbol.upper(),
            price_usd=price_usd,
            price_toman=price_toman,
            timestamp=data.get("timestamp"),
            raw=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {e}")