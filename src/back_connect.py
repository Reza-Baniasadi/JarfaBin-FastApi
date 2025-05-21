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