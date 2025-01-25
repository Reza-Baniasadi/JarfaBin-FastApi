from pydantic import BaseModel

class CryptoCurrencyBase(BaseModel):
    name: str
    symbol: str

class CryptoCurrencyCreate(CryptoCurrencyBase):
    pass

class CryptoCurrency(CryptoCurrencyBase):
    id: int
    price_usd: float

    class Config:
        orm_mode = True

class UserCryptoBase(BaseModel):
    crypto_id: int
    amount: float

class UserCryptoCreate(UserCryptoBase):
    pass

class UserCrypto(UserCryptoBase):
    id: int
    user_id: int
    crypto: CryptoCurrency

    class Config:
        orm_mode = True