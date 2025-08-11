import os
from enum import Enum
from typing import Optional

from pydantic import BaseSettings, SecretStr, EmailStr
from starlette.config import Config

# بارگذاری فایل env
current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: Optional[str] = config("APP_DESCRIPTION", default=None)
    APP_VERSION: Optional[str] = config("APP_VERSION", default=None)
    LICENSE_NAME: Optional[str] = config("LICENSE", default=None)
    CONTACT_NAME: Optional[str] = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: Optional[str] = config("CONTACT_EMAIL", default=None)


class CryptSettings(BaseSettings):
    SECRET_KEY: SecretStr = config("SECRET_KEY", cast=SecretStr)
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URI: str = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    POSTGRES_URL: Optional[str] = config("POSTGRES_URL", default=None)


class FirstUserSettings(BaseSettings):
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: EmailStr = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class RedisSettings(BaseSettings):
    HOST: str = config("REDIS_HOST", default="localhost")
    PORT: int = config("REDIS_PORT", default=6379)
    URL: str = f"redis://{HOST}:{PORT}"


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


class CRUDAdminSettings(BaseSettings):
    ENABLED: bool = config("CRUD_ADMIN_ENABLED", default=True)
    MOUNT_PATH: str = config("CRUD_ADMIN_MOUNT_PATH", default="/admin")
    ALLOWED_IPS_LIST: Optional[list[str]] = None
    ALLOWED_NETWORKS_LIST: Optional[list[str]] = None
    MAX_SESSIONS: int = config("CRUD_ADMIN_MAX_SESSIONS", default=10)
    SESSION_TIMEOUT: int = config("CRUD_ADMIN_SESSION_TIMEOUT", default=1440)
    SECURE_COOKIES: bool = config("SESSION_SECURE_COOKIES", default=True)
    TRACK_EVENTS: bool = config("CRUD_ADMIN_TRACK_EVENTS", default=True)
    TRACK_SESSIONS: bool = config("CRUD_ADMIN_TRACK_SESSIONS", default=True)
    REDIS_ENABLED: bool = config("CRUD_ADMIN_REDIS_ENABLED", default=False)
    REDIS_HOST: str = config("CRUD_ADMIN_REDIS_HOST", default="localhost")
    REDIS_PORT: int = config("CRUD_ADMIN_REDIS_PORT", default=6379)
    REDIS_DB: int = config("CRUD_ADMIN_REDIS_DB", default=0)
    REDIS_PASSWORD: Optional[str] = config("CRUD_ADMIN_REDIS_PASSWORD", default=None)
    REDIS_SSL: bool = config("CRUD_ADMIN_REDIS_SSL", default=False)