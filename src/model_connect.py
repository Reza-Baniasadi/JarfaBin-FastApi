from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class CryptoPriceResponse(BaseModel):
    symbol: str
    price_usd: float
    price_toman: Optional[float] = None
    timestamp: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

class ModelRequest(BaseModel):
    text: Optional[str] = None
    features: Optional[Dict[str, Any]] = None