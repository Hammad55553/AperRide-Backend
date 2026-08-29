# AsperRide — Deploy + App Integration Guide

Ye guide 3 cheezein cover karti hai: (1) Supabase database, (2) Vercel deploy,
(3) React Native app ko live backend se jodna.

> NOTE: Vercel par **socket.io band hai** (serverless WebSocket support nahi karta).
> Isliye live-tracking / bidding / in-app chat abhi app me MOCK par chal rahe hain.
> REST features — login, register, ride create, nearby drivers, fare, trip history,
> wallet, rating — sab REAL backend se jud gaye hain.
> Socket wapas chahiye to backend Render/Railway par deploy karna (Dockerfile ready hai).

---

## 1) Supabase database (ek baar)

1. Supabase project kholo → **SQL Editor**.
2. `db/supabase_schema.sql` ka poora content paste karke **Run** karo.
   - PostGIS + pgcrypto extensions
   - saari tables (users, drivers, rides, ride_bids, ratings, wallet_txs)
   - geo index (GIST on drivers.location)
3. Connection string lo: **Settings → Database → Connection string → URI**.
   - Us URI ko asyncpg format me convert karo:
     `postgresql://...`  ->  `postgresql+asyncpg://...`
   - Example:
     ```
     postgresql+asyncpg://postgres.xxxx:YOUR_PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres
     ```

## 2) Vercel deploy

1. vercel.com → **Add New → Project** → GitHub repo `AperRide-Backend` import.
2. Framework preset: **Other** (vercel.json khud detect ho jayega).
3. **Environment Variables** set karo:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Supabase asyncpg URL (upar wala) |
   | `JWT_SECRET` | koi lamba random string |
   | `JWT_ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
   | `ENV` | `staging` |
   | `CORS_ORIGINS` | `*` |

4. **Deploy** dabao. Live URL milega, e.g. `https://aper-ride-backend.vercel.app`
5. Test: browser me `https://<your-url>/health` kholo → `{"status":"healthy"}` aana chahiye.
   Aur `https://<your-url>/docs` → Swagger API docs.

## 3) App ko live URL se jodo

App me sirf **ek file** change karni hai:

`ApniRide/src/config/apiConfig.ts`

```ts
// Ye line badlo:
export const API_HOST = 'https://<your-vercel-url>';   // no trailing slash
```

Bas. App restart karo — login/register/rides/wallet ab live backend se chalenge.

> Local testing ke liye (Vercel se pehle): Android emulator par `http://10.0.2.2:8000`
> aur `uvicorn app.main:asgi --reload` chalao.

---

## Kya live hai vs mock (is stage par)

| Feature | Status |
|---------|--------|
| Login / OTP / Register | ✅ REST (live) |
| Ride create + suggested fare | ✅ REST |
| Nearby drivers (PostGIS) | ✅ REST |
| Trip history (rider + driver) | ✅ REST |
| Wallet balance / tx / withdraw | ✅ REST |
| Driver online toggle | ✅ REST |
| Rating submit | ✅ REST |
| Live driver tracking on map | ⏳ mock (socket needed) |
| Real-time bidding | ⏳ mock (socket needed) |
| In-app chat | ⏳ mock (socket needed) |

Socket features enable karne ke liye backend ko Render/Railway par deploy karo
(`Dockerfile`, `render.yaml` ready hain) aur `apiConfig.ts` ka `API_HOST` us URL par set karo.
