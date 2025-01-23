from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CryptoCurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    symbol = Column(String, unique=True, index=True)
    price_usd = Column(Float)