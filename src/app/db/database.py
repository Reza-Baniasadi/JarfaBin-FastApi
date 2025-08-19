from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from ..config import settings


class BaseModel(DeclarativeBase, MappedAsDataclass):
    """Base class for all ORM models with dataclass mapping."""
    pass


POSTGRES_URI = settings.POSTGRES_URI
POSTGRES_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{POSTGRES_PREFIX}{POSTGRES_URI}"

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator that yields a database session.
    Usage: 
        async with get_async_db() as db:
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
