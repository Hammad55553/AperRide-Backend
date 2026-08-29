from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_driver
from app.models import Driver, WalletTx
from app.schemas.driver import WithdrawRequest

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/balance")
async def balance(driver: Driver = Depends(get_current_driver)):
    return {"wallet_balance": float(driver.wallet_balance), "rating": float(driver.rating)}


@router.get("/transactions")
async def transactions(driver: Driver = Depends(get_current_driver),
                       db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(WalletTx).where(WalletTx.driver_id == driver.id).order_by(WalletTx.created_at.desc())
    )
    return [
        {"id": str(t.id), "type": t.type.value, "amount": float(t.amount),
         "note": t.note, "created_at": t.created_at.isoformat()}
        for t in rows
    ]


@router.post("/withdraw")
async def withdraw(body: WithdrawRequest, driver: Driver = Depends(get_current_driver),
                   db: AsyncSession = Depends(get_db)):
    from app.models.wallet_tx import TxType
    if body.amount > float(driver.wallet_balance):
        return {"detail": "Insufficient balance"}
    tx = WalletTx(driver_id=driver.id, type=TxType.withdrawal, amount=body.amount,
                  note=f"Withdraw to {body.account}")
    driver.wallet_balance = float(driver.wallet_balance) - body.amount
    db.add(tx)
    await db.commit()
    return {"detail": "Withdrawal requested", "new_balance": float(driver.wallet_balance)}
