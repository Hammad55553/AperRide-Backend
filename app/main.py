import socketio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, drivers, rides, wallet
from app.realtime.socket import sio
from app.realtime.keepalive import start_keepalive


@asynccontextmanager
async def lifespan(app: FastAPI):
    # PostGIS + tables are managed by Alembic migrations in production.
    task = start_keepalive(settings.SELF_PING_URL, settings.SELF_PING_INTERVAL_SEC)
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="AsperRide API",
    description="Ride-hailing backend for Hasilpur — by Asper Infotech",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")
app.include_router(rides.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")


@app.get("/")
async def root():
    return {"app": "AsperRide API", "status": "ok", "env": settings.ENV}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Wrap FastAPI with Socket.IO ASGI app -> single deployable
asgi = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/socket.io")
