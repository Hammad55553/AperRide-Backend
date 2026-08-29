import uuid
from pydantic import BaseModel, Field
from app.schemas.common import LatLng


class DriverRegister(BaseModel):
    vehicle_type: str
    vehicle_plate: str
    vehicle_model: str | None = None
    vehicle_color: str | None = None


class DriverOut(BaseModel):
    id: uuid.UUID
    vehicle_type: str
    vehicle_plate: str
    is_online: bool
    is_verified: bool
    rating: float
    wallet_balance: float

    class Config:
        from_attributes = True


class OnlineToggle(BaseModel):
    is_online: bool


class LocationUpdate(BaseModel):
    location: LatLng


class WithdrawRequest(BaseModel):
    amount: float = Field(gt=0)
    account: str
