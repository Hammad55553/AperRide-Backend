import uuid
import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Float, String, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TxType(str, enum.Enum):
    earning = "earning"
    bonus = "bonus"
    withdrawal = "withdrawal"
    fee = "fee"


class WalletTx(Base):
    __tablename__ = "wallet_txs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("drivers.id"), index=True)
    ride_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("rides.id"), nullable=True)

    type: Mapped[TxType] = mapped_column(Enum(TxType))
    amount: Mapped[float] = mapped_column(Float)  # +earning/bonus, -withdrawal/fee
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
