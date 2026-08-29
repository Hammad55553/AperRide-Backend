from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user, get_current_driver
from app.models import User, Driver
from app.schemas.driver import DriverRegister, DriverOut, OnlineToggle, LocationUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post("/register", response_model=DriverOut, status_code=201)
async def register_driver(body: DriverRegister, user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(Driver).where(Driver.user_id == user.id))
    if existing:
        raise HTTPException(409, "Driver profile already exists")
    driver = Driver(user_id=user.id, **body.model_dump())
    user.is_driver = True
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return DriverOut.model_validate(driver)


@router.get("/me", response_model=DriverOut)
async def me(driver: Driver = Depends(get_current_driver)):
    return DriverOut.model_validate(driver)


@router.patch("/online", response_model=DriverOut)
async def toggle_online(body: OnlineToggle, driver: Driver = Depends(get_current_driver),
                        db: AsyncSession = Depends(get_db)):
    driver.is_online = body.is_online
    await db.commit()
    await db.refresh(driver)
    return DriverOut.model_validate(driver)


@router.patch("/location")
async def update_location(body: LocationUpdate, driver: Driver = Depends(get_current_driver),
                          db: AsyncSession = Depends(get_db)):
    driver.location = ST_SetSRID(
        ST_MakePoint(body.location.longitude, body.location.latitude), 4326
    )
    await db.commit()
    return {"detail": "location updated"}
