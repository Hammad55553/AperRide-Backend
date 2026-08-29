import uuid
from pydantic import BaseModel, Field
from app.schemas.common import LatLng


class RideCreate(BaseModel):
    pickup: LatLng
    dropoff: LatLng
    pickup_address: str | None = None
    dropoff_address: str | None = None
    vehicle_type: str = "Mini"
    rider_offer: float | None = None


class RideOut(BaseModel):
    id: uuid.UUID
    rider_id: uuid.UUID
    driver_id: uuid.UUID | None
    vehicle_type: str
    suggested_fare: float | None
    rider_offer: float | None
    final_fare: float | None
    status: str
    pickup_address: str | None
    dropoff_address: str | None
    distance_m: float | None
    duration_s: float | None

    class Config:
        from_attributes = True


class BidCreate(BaseModel):
    price: float = Field(gt=0)
    eta_min: int = Field(ge=1, le=60)


class BidOut(BaseModel):
    id: uuid.UUID
    driver_id: uuid.UUID
    price: float
    eta_min: int

    class Config:
        from_attributes = True


class NearbyDriver(BaseModel):
    driver_id: uuid.UUID
    vehicle_type: str
    latitude: float
    longitude: float
    distance_m: float
    rating: float


class RatingCreate(BaseModel):
    stars: int = Field(ge=1, le=5)
    tip: float = Field(default=0, ge=0)
    comment: str | None = None
