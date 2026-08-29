import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    vehicle_type: Mapped[str] = mapped_column(String(40))   # Moto, Rickshaw, Mini, Premium ...
    vehicle_plate: Mapped[str] = mapped_column(String(20))
    vehicle_model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    vehicle_color: Mapped[str | None] = mapped_column(String(40), nullable=True)

    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=5.0)
    wallet_balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    # PostGIS point (lon lat), SRID 4326 geography = accurate metres for distance
    location: Mapped[str | None] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="driver")
