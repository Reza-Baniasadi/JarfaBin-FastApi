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

async def fetch_arzdigital_price(symbol: str) -> dict:
    headers = {}
    if settings.ARZDIGITAL_API_KEY:
        headers["Authorization"] = f"Bearer {settings.ARZDIGITAL_API_KEY}"