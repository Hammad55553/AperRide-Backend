from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# psycopg (v3) async driver — Vercel serverless par asyncpg/uvloop masle se bachne ke liye.
# NullPool: har serverless invocation apna connection banaye. sslmode=require Supabase ke liye.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"sslmode": "require", "prepare_threshold": None},
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
