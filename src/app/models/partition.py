from sqlalchemy import Column, String, Integer, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Partition(Base):
    __tablename__ = 'partitions'

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(512))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    size_bytes = Column(BigInteger, default=0)
    record_count = Column(BigInteger, default=0)