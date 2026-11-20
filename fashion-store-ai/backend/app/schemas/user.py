from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    phone: Optional[str] = None
    otp: Optional[str] = None


class RegisterSendOtpRequest(BaseModel):
    email: EmailStr


class RegisterVerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class SendOtpRequest(BaseModel):
    email_or_phone: str


class VerifyOtpRequest(BaseModel):
    email_or_phone: str
    otp: str


class ResetPasswordRequest(BaseModel):
    email_or_phone: str
    otp: str
    new_password: str = Field(min_length=6)


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    phone: Optional[str] = None
    role: str = "customer"
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)
