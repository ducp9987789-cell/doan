from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import get_current_user
from app.schemas.user import (
    ChangePasswordRequest,
    RegisterSendOtpRequest,
    RegisterVerifyOtpRequest,
    ResetPasswordRequest,
    SendOtpRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
    UserUpdate,
    VerifyOtpRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/send-otp")
async def send_register_otp(payload: RegisterSendOtpRequest) -> dict:
    return await UserService.send_register_otp(payload)


@router.post("/register/verify-otp")
async def verify_register_otp(payload: RegisterVerifyOtpRequest) -> dict:
    return await UserService.verify_register_otp(payload)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister) -> dict:
    return await UserService.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    return await UserService.login(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(payload: UserUpdate, current_user: dict = Depends(get_current_user)) -> dict:
    return await UserService.update_profile(current_user["id"], payload)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await UserService.change_password(current_user["id"], payload)


@router.post("/forgot-password/send-otp")
async def send_forgot_otp(payload: SendOtpRequest) -> dict:
    return await UserService.send_forgot_otp(payload)


@router.post("/forgot-password/verify-otp")
async def verify_forgot_otp(payload: VerifyOtpRequest) -> dict:
    return await UserService.verify_forgot_otp(payload)


@router.post("/forgot-password/reset")
async def reset_password(payload: ResetPasswordRequest) -> dict:
    return await UserService.reset_password(payload)
