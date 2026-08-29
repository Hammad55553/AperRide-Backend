import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# Supabase transaction pooler (port 6543) + Vercel serverless.
#  - NullPool: serverless me connection pool nahi rakhte
#  - prepared statements OFF: pgbouncer transaction mode ke liye zaroori
#  - unique prepared_statement_name_func: pgbouncer name-collision se bache
#  - SSL context: Supabase SSL enforce karta hai
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "ssl": _ssl_ctx,
        "server_settings": {"jit": "off"},
    },
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
