from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal


app = FastAPI(title="Crypto File Utils API", version="0.1.0")