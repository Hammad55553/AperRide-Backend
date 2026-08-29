# AsperRide Backend

Ride-hailing API for **Hasilpur, Punjab** — built by **Asper Infotech**.
InDrive-style bidding, live driver tracking, and PostGIS-based driver matching.

**Stack:** FastAPI · SQLAlchemy 2.0 (async) · asyncpg · PostGIS (GeoAlchemy2) · Socket.IO · JWT · Alembic
**Database:** Supabase (PostgreSQL + PostGIS) · **Deploy:** Railway

---

## Folder structure

```
AsperRide-Backend/
├── app/
│   ├── main.py            # FastAPI + Socket.IO ASGI entrypoint (app.main:asgi)
│   ├── config.py          # pydantic-settings — env config
│   ├── database.py        # async engine, session, Base
│   ├── core/
│   │   ├── security.py    # bcrypt hashing, JWT create/decode
│   │   └── deps.py        # get_current_user / get_current_driver
│   ├── models/            # SQLAlchemy ORM tables
│   │   ├── user.py  driver.py  ride.py  ride_bid.py  rating.py  wallet_tx.py
│   ├── schemas/           # Pydantic request/response models
│   │   ├── auth.py  ride.py  driver.py  common.py
│   ├── services/          # business logic
│   │   ├── fare.py        # fare calc + surge + 15% commission (matches app)
│   │   └── geo.py         # nearby-driver PostGIS ST_DWithin query
│   ├── routers/           # API endpoints
│   │   ├── auth.py  drivers.py  rides.py  wallet.py
│   └── realtime/
│       └── socket.py      # Socket.IO events (location, bids, chat, status)
├── alembic/               # DB migrations
├── tests/
├── Dockerfile  Procfile  railway.json
└── requirements.txt
```

## Ride flow

```
Rider requests ride ──► POST /api/rides  (suggested fare + rider_offer)
        │
        ▼
Nearby online drivers ◄── GET /api/rides/nearby-drivers  (PostGIS ST_DWithin)
        │
        ▼
Drivers bid ──► POST /api/rides/{id}/bids  ──►  socket "new_bid" to rider
        │
        ▼
Rider accepts ──► POST /api/rides/{id}/accept?bid_id=  (status=accepted)
        │
        ▼
Live tracking  ──►  socket "driver_location" ⇄ "driver_moved"
Chat           ──►  socket "chat_message"
        │
        ▼
Complete ──► POST /api/rides/{id}/status  ──►  Rating ──► POST /api/rides/{id}/rate
```

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill DATABASE_URL + JWT_SECRET

# one-time on the database:  CREATE EXTENSION IF NOT EXISTS postgis;
alembic revision --autogenerate -m "init"
alembic upgrade head

uvicorn app.main:asgi --reload    # http://localhost:8000/docs
```

## Key endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register` `/login` `/otp/request` `/otp/verify` | Auth |
| POST | `/api/drivers/register` · PATCH `/online` `/location` | Driver profile |
| GET  | `/api/rides/nearby-drivers` | Find drivers (geo) |
| POST | `/api/rides` | Create ride request |
| POST | `/api/rides/{id}/bids` · GET `/bids` · POST `/accept` | Bidding |
| POST | `/api/rides/{id}/status` `/rate` | Trip lifecycle |
| GET  | `/api/wallet/balance` `/transactions` · POST `/withdraw` | Driver wallet |

## Deploy (Railway)

1. Add a Supabase database, enable PostGIS (`CREATE EXTENSION postgis;`).
2. Set env vars from `.env.example` in Railway.
3. Push — Railway builds the Dockerfile, runs migrations, starts the ASGI app.

Socket.IO is served on the same service at `/socket.io`.
