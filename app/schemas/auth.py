import uuid
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=20)
    email: EmailStr | None = None
    password: str | None = Field(default=None, max_length=128)
    is_driver: bool = False


class LoginRequest(BaseModel):
    phone: str
    password: str


class OtpRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)


class OtpVerify(BaseModel):
    phone: str
    code: str = Field(min_length=4, max_length=6)


class UserOut(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: str
    email: str | None = None
    is_driver: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
