-- ============================================================
-- AsperRide — Supabase schema (run ONCE in SQL editor)
-- ============================================================

-- 1) Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()

-- 2) Enums
DO $$ BEGIN
  CREATE TYPE ridestatus AS ENUM ('requested','accepted','ongoing','completed','cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE txtype AS ENUM ('earning','bonus','withdrawal','fee');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 3) Tables
CREATE TABLE IF NOT EXISTS users (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(160),
    hashed_password VARCHAR(255),
    is_driver BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (phone)
);

CREATE TABLE IF NOT EXISTS drivers (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    vehicle_type VARCHAR(40) NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL,
    vehicle_model VARCHAR(80),
    vehicle_color VARCHAR(40),
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    rating NUMERIC(3, 2) NOT NULL DEFAULT 5.0,
    wallet_balance NUMERIC(10, 2) NOT NULL DEFAULT 0,
    location geography(POINT,4326),
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (user_id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS rides (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    rider_id UUID NOT NULL,
    driver_id UUID,
    pickup geography(POINT,4326) NOT NULL,
    dropoff geography(POINT,4326) NOT NULL,
    pickup_address VARCHAR(255),
    dropoff_address VARCHAR(255),
    vehicle_type VARCHAR(40) NOT NULL,
    suggested_fare FLOAT,
    rider_offer FLOAT,
    final_fare FLOAT,
    distance_m FLOAT,
    duration_s FLOAT,
    status ridestatus NOT NULL DEFAULT 'requested',
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    completed_at TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (rider_id) REFERENCES users (id),
    FOREIGN KEY (driver_id) REFERENCES drivers (id)
);

CREATE TABLE IF NOT EXISTS ride_bids (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    ride_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    price FLOAT NOT NULL,
    eta_min INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (ride_id) REFERENCES rides (id),
    FOREIGN KEY (driver_id) REFERENCES drivers (id)
);

CREATE TABLE IF NOT EXISTS ratings (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    ride_id UUID NOT NULL,
    rider_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    stars INTEGER NOT NULL,
    tip FLOAT NOT NULL DEFAULT 0,
    comment VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (ride_id) REFERENCES rides (id),
    FOREIGN KEY (rider_id) REFERENCES users (id),
    FOREIGN KEY (driver_id) REFERENCES drivers (id)
);

CREATE TABLE IF NOT EXISTS wallet_txs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL,
    ride_id UUID,
    type txtype NOT NULL,
    amount FLOAT NOT NULL,
    note VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (driver_id) REFERENCES drivers (id),
    FOREIGN KEY (ride_id) REFERENCES rides (id)
);

-- 4) Indexes (geo search + lookups)
CREATE INDEX IF NOT EXISTS idx_drivers_location ON drivers USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_drivers_online   ON drivers (is_online);
CREATE INDEX IF NOT EXISTS idx_rides_status     ON rides (status);
CREATE INDEX IF NOT EXISTS idx_rides_rider      ON rides (rider_id);
CREATE INDEX IF NOT EXISTS idx_bids_ride        ON ride_bids (ride_id);
