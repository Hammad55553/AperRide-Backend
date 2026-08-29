from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import (
    RegisterRequest, LoginRequest, OtpRequest, OtpVerify, TokenResponse, UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.phone == body.phone))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Phone already registered")
    user = User(
        full_name=body.full_name,
        phone=body.phone,
        email=body.email,
        hashed_password=hash_password(body.password) if body.password else None,
        is_driver=body.is_driver,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.phone == body.phone))
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/otp/request")
async def otp_request(body: OtpRequest):
    # TODO integrate SMS gateway (Twilio). Dev returns a fixed code.
    return {"detail": "OTP sent", "dev_code": "123456"}


@router.post("/otp/verify", response_model=TokenResponse)
async def otp_verify(body: OtpVerify, db: AsyncSession = Depends(get_db)):
    if body.code != "123456":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid code")
    user = await db.scalar(select(User).where(User.phone == body.phone))
    if not user:
        user = User(full_name="AsperRide User", phone=body.phone, is_phone_verified=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/debug/db")
async def debug_db(db: AsyncSession = Depends(get_db)):
    """TEMP: real DB error text dekhne ke liye. Baad me hata denge."""
    from sqlalchemy import text
    try:
        r = await db.execute(text("select 1"))
        return {"db": "ok", "result": r.scalar()}
    except Exception as e:
        import traceback
        return {"db": "FAIL", "error_type": type(e).__name__,
                "error": str(e), "trace": traceback.format_exc()[-1500:]}
