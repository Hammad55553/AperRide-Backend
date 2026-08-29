from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user, get_current_driver
from app.models import User, Driver, Ride, RideStatus, RideBid, Rating
from app.schemas.ride import (
    RideCreate, RideOut, BidCreate, BidOut, NearbyDriver, RatingCreate,
)
from app.services.fare import estimate_fare, split_fare
from app.services.geo import nearby_drivers

router = APIRouter(prefix="/rides", tags=["rides"])


def _point(lat, lng):
    return ST_SetSRID(ST_MakePoint(lng, lat), 4326)


@router.get("/nearby-drivers", response_model=list[NearbyDriver])
async def get_nearby(lat: float = Query(...), lng: float = Query(...),
                     vehicle_type: str | None = None, radius_m: int = 3000,
                     db: AsyncSession = Depends(get_db)):
    rows = await nearby_drivers(db, lat, lng, radius_m, vehicle_type)
    return [NearbyDriver(**r) for r in rows]


@router.post("", response_model=RideOut, status_code=201)
async def create_ride(body: RideCreate, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    # rough straight-line estimate for suggested fare (client refines with OSRM)
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000
    dlat = radians(body.dropoff.latitude - body.pickup.latitude)
    dlng = radians(body.dropoff.longitude - body.pickup.longitude)
    a = sin(dlat / 2) ** 2 + cos(radians(body.pickup.latitude)) * cos(
        radians(body.dropoff.latitude)) * sin(dlng / 2) ** 2
    dist_m = R * 2 * atan2(sqrt(a), sqrt(1 - a))
    dur_s = dist_m / 8.3  # ~30 km/h
    suggested = estimate_fare(dist_m, dur_s, body.vehicle_type)

    ride = Ride(
        rider_id=user.id,
        pickup=_point(body.pickup.latitude, body.pickup.longitude),
        dropoff=_point(body.dropoff.latitude, body.dropoff.longitude),
        pickup_address=body.pickup_address,
        dropoff_address=body.dropoff_address,
        vehicle_type=body.vehicle_type,
        suggested_fare=suggested,
        rider_offer=body.rider_offer,
        distance_m=dist_m,
        duration_s=dur_s,
        status=RideStatus.requested,
    )
    db.add(ride)
    await db.commit()
    await db.refresh(ride)
    return RideOut.model_validate(ride)


@router.get("/{ride_id}", response_model=RideOut)
async def get_ride(ride_id: str, db: AsyncSession = Depends(get_db)):
    ride = await db.get(Ride, ride_id)
    if not ride:
        raise HTTPException(404, "Ride not found")
    return RideOut.model_validate(ride)


@router.post("/{ride_id}/bids", response_model=BidOut, status_code=201)
async def place_bid(ride_id: str, body: BidCreate, driver: Driver = Depends(get_current_driver),
                    db: AsyncSession = Depends(get_db)):
    ride = await db.get(Ride, ride_id)
    if not ride or ride.status != RideStatus.requested:
        raise HTTPException(400, "Ride not open for bids")
    bid = RideBid(ride_id=ride.id, driver_id=driver.id, price=body.price, eta_min=body.eta_min)
    db.add(bid)
    await db.commit()
    await db.refresh(bid)
    return BidOut.model_validate(bid)


@router.get("/{ride_id}/bids", response_model=list[BidOut])
async def list_bids(ride_id: str, db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(RideBid).where(RideBid.ride_id == ride_id))
    return [BidOut.model_validate(b) for b in rows]


@router.post("/{ride_id}/accept", response_model=RideOut)
async def accept_bid(ride_id: str, bid_id: str = Query(...),
                     user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ride = await db.get(Ride, ride_id)
    bid = await db.get(RideBid, bid_id)
    if not ride or not bid or bid.ride_id != ride.id:
        raise HTTPException(404, "Ride or bid not found")
    if ride.rider_id != user.id:
        raise HTTPException(403, "Not your ride")
    ride.driver_id = bid.driver_id
    ride.final_fare = bid.price
    ride.status = RideStatus.accepted
    await db.commit()
    await db.refresh(ride)
    return RideOut.model_validate(ride)


@router.post("/{ride_id}/status", response_model=RideOut)
async def update_status(ride_id: str, status: RideStatus,
                        driver: Driver = Depends(get_current_driver),
                        db: AsyncSession = Depends(get_db)):
    ride = await db.get(Ride, ride_id)
    if not ride or ride.driver_id != driver.id:
        raise HTTPException(403, "Not your ride")
    ride.status = status
    await db.commit()
    await db.refresh(ride)
    return RideOut.model_validate(ride)


@router.post("/{ride_id}/rate", status_code=201)
async def rate_ride(ride_id: str, body: RatingCreate, user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    ride = await db.get(Ride, ride_id)
    if not ride or not ride.driver_id:
        raise HTTPException(404, "Ride not found")
    rating = Rating(ride_id=ride.id, rider_id=user.id, driver_id=ride.driver_id,
                    stars=body.stars, tip=body.tip, comment=body.comment)
    db.add(rating)
    await db.commit()
    return {"detail": "Thanks for rating"}
