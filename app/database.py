import socket
from urllib.parse import urlsplit
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def _ipv4_connect_args(url: str) -> dict:
    """
    Vercel serverless IPv6 outbound block karta hai, aur Supabase pooler
    hostname IPv6 par resolve hota hai -> 'Device or resource busy'.
    Isliye hostname ko IPv4 par resolve karke psycopg ko hostaddr dete hain.
    """
    args = {"sslmode": "require", "prepare_threshold": None}
    try:
        host = urlsplit(url).hostname
        if host:
            info = socket.getaddrinfo(host, None, socket.AF_INET)  # IPv4 only
            if info:
                args["hostaddr"] = info[0][4][0]
    except Exception:
        pass  # resolve fail -> normal connection try hogi
    return args


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args=_ipv4_connect_args(settings.DATABASE_URL),
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
