import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseSettings
import httpx
from models import CryptoPriceResponse, ModelRequest, ModelResponse
from typing import Optional