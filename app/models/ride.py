import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.database import Base


class RideStatus(str, enum.Enum):
    requested = "requested"     # rider sent offer, drivers bidding
    accepted = "accepted"       # a bid accepted, driver assigned
    ongoing = "ongoing"         # trip in progress
    completed = "completed"
    cancelled = "cancelled"


class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    driver_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True, index=True)

    pickup: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    dropoff: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    pickup_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dropoff_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    vehicle_type: Mapped[str] = mapped_column(String(40))
    suggested_fare: Mapped[float | None] = mapped_column(Float, nullable=True)
    rider_offer: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_fare: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[RideStatus] = mapped_column(Enum(RideStatus), default=RideStatus.requested, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    bids = relationship("RideBid", back_populates="ride", cascade="all, delete-orphan")
