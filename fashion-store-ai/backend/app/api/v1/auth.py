import random
from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import ReturnDocument

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.core.utils import serialize_doc
from app.db.mongodb import get_database
from app.db.redis import get_redis
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
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/send-otp")
async def send_register_otp(payload: RegisterSendOtpRequest) -> dict:
    db = get_database()
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi một tài khoản khác.")

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(seconds=60)

    redis = get_redis()
    if redis is not None:
        try:
            await redis.setex(f"register_otp:{email}", 60, otp)
        except Exception:
            pass

    await db.register_otps.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                "otp": otp,
                "expires_at": expires_at,
                "verified": False,
                "created_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    email_res = EmailService.send_otp_email(to_email=email, otp=otp, purpose="register")
    if not email_res.get("success", False):
        err_msg = email_res.get("error") or "Không thể gửi email OTP."
        raise HTTPException(
            status_code=500,
            detail=f"Không thể gửi mã OTP tới email {email}. Chi tiết lỗi: {err_msg}. Vui lòng kiểm tra cấu hình SMTP trong backend/.env!"
        )

    return {
        "success": True,
        "message": f"Mã xác thực OTP đã được gửi vào hộp thư Gmail của bạn ({email}). Vui lòng kiểm tra email để lấy mã xác nhận!",
    }


@router.post("/register/verify-otp")
async def verify_register_otp(payload: RegisterVerifyOtpRequest) -> dict:
    db = get_database()
    email = payload.email.lower().strip()
    otp_val = payload.otp.strip()

    verified = False
    redis = get_redis()
    if redis is not None:
        try:
            stored_otp = await redis.get(f"register_otp:{email}")
            if stored_otp and stored_otp == otp_val:
                verified = True
        except Exception:
            pass

    if not verified:
        record = await db.register_otps.find_one({
            "email": email,
            "otp": otp_val,
            "expires_at": {"$gt": datetime.utcnow()},
        })
        if record:
            verified = True

    if not verified:
        raise HTTPException(
            status_code=400,
            detail="Mã OTP không chính xác hoặc đã hết hạn hiệu lực (1 phút). Vui lòng nhấn gửi lại mã mới!"
        )

    if redis is not None:
        try:
            await redis.setex(f"register_verified:{email}", 600, "1")
        except Exception:
            pass

    await db.register_otps.update_one(
        {"email": email},
        {"$set": {"verified": True, "verified_at": datetime.utcnow()}},
    )

    return {
        "success": True,
        "message": "Xác thực email thành công! Bạn có thể tiếp tục hoàn tất tạo tài khoản.",
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister) -> dict:
    db = get_database()
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Kiểm tra mã OTP gửi kèm
    otp_val = (payload.otp or "").strip()
    verified = False
    redis = get_redis()

    if otp_val:
        if redis is not None:
            try:
                stored = await redis.get(f"register_otp:{email}")
                if stored and stored == otp_val:
                    verified = True
            except Exception:
                pass
        if not verified:
            rec = await db.register_otps.find_one({
                "email": email,
                "otp": otp_val,
                "expires_at": {"$gt": datetime.utcnow()},
            })
            if rec:
                verified = True

    if not verified:
        # Kiểm tra nếu đã xác thực qua verify-otp trước đó
        if redis is not None:
            try:
                val = await redis.get(f"register_verified:{email}")
                if val:
                    verified = True
            except Exception:
                pass
        if not verified:
            rec_v = await db.register_otps.find_one({
                "email": email,
                "verified": True,
                "verified_at": {"$gt": datetime.utcnow() - timedelta(minutes=10)},
            })
            if rec_v:
                verified = True

    if not verified:
        raise HTTPException(
            status_code=400,
            detail="Mã OTP không chính xác hoặc đã quá hạn 1 phút. Vui lòng bấm 'Gửi mã OTP' để nhận mã mới.",
        )

    doc = {
        "email": email,
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "role": "customer",
        "phone": payload.phone,
        "address": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Dọn dẹp trạng thái OTP
    if redis is not None:
        try:
            await redis.delete(f"register_verified:{email}", f"register_otp:{email}")
        except Exception:
            pass
    await db.register_otps.delete_many({"email": email})

    return serialize_doc(doc)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    db = get_database()
    user = await db.users.find_one({"email": form_data.username.lower()})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is disabled")
    token = create_access_token(str(user["_id"]), extra={"role": user["role"]})
    user_data = serialize_doc(user)
    return {"access_token": token, "token_type": "bearer", "user": user_data}


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(payload: UserUpdate, current_user: dict = Depends(get_current_user)) -> dict:
    db = get_database()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if "email" in updates and updates["email"]:
        updates["email"] = updates["email"].lower()
        existing = await db.users.find_one({
            "email": updates["email"],
            "_id": {"$ne": ObjectId(current_user["id"])}
        })
        if existing:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi tài khoản khác")

    updates["updated_at"] = datetime.utcnow()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(current_user["id"])},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_doc(result)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin người dùng")

    if not verify_password(payload.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác")

    new_hash = hash_password(payload.new_password)
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}},
    )
    return {"message": "Đổi mật khẩu thành công! Vui lòng ghi nhớ mật khẩu mới."}


@router.post("/forgot-password/send-otp")
async def send_forgot_otp(payload: SendOtpRequest) -> dict:
    db = get_database()
    query_val = payload.email_or_phone.strip()
    if not query_val:
        raise HTTPException(status_code=400, detail="Vui lòng nhập email hoặc số điện thoại")

    user = await db.users.find_one({
        "$or": [
            {"email": query_val.lower()},
            {"phone": query_val},
        ]
    })
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản nào khớp với email hoặc số điện thoại này."
        )

    # Sinh mã OTP 6 chữ số ngẫu nhiên
    otp = str(random.randint(100000, 999999))
    user_key = str(user["_id"])
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Lưu vào Redis nếu có
    redis = get_redis()
    if redis is not None:
        try:
            await redis.setex(f"forgot_otp:{user_key}", 300, otp)
        except Exception:
            pass

    # Lưu dự phòng vào MongoDB collection password_resets
    await db.password_resets.update_one(
        {"user_id": user_key},
        {
            "$set": {
                "user_id": user_key,
                "email": user.get("email"),
                "phone": user.get("phone"),
                "otp": otp,
                "expires_at": expires_at,
                "verified": False,
                "created_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    if not user.get("email"):
        raise HTTPException(
            status_code=400,
            detail="Tài khoản này chưa có thông tin email để nhận mã OTP."
        )

    email_res = EmailService.send_otp_email(to_email=user["email"], otp=otp, purpose="forgot")
    if not email_res.get("success", False):
        err_msg = email_res.get("error") or "Không thể gửi email OTP."
        raise HTTPException(
            status_code=500,
            detail=f"Không thể gửi mã OTP tới email {user['email']}. Chi tiết lỗi: {err_msg}. Vui lòng kiểm tra cấu hình SMTP trong backend/.env!"
        )

    return {
        "success": True,
        "message": f"Mã xác thực OTP đã được gửi đến email {user['email']}. Vui lòng kiểm tra hộp thư của bạn!",
        "email_or_phone": query_val,
    }


@router.post("/forgot-password/verify-otp")
async def verify_forgot_otp(payload: VerifyOtpRequest) -> dict:
    db = get_database()
    query_val = payload.email_or_phone.strip()
    otp_val = payload.otp.strip()

    user = await db.users.find_one({
        "$or": [
            {"email": query_val.lower()},
            {"phone": query_val},
        ]
    })
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản tương ứng.")

    user_key = str(user["_id"])
    matched = False

    # Kiểm tra qua Redis
    redis = get_redis()
    if redis is not None:
        try:
            stored_otp = await redis.get(f"forgot_otp:{user_key}")
            if stored_otp and stored_otp == otp_val:
                matched = True
        except Exception:
            pass

    # Nếu Redis chưa khớp, kiểm tra MongoDB
    if not matched:
        reset_doc = await db.password_resets.find_one({"user_id": user_key})
        if reset_doc and reset_doc.get("otp") == otp_val:
            if reset_doc.get("expires_at") and reset_doc["expires_at"] > datetime.utcnow():
                matched = True

    if not matched:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác hoặc đã hết hạn.")

    # Đánh dấu đã xác thực OTP trong DB
    await db.password_resets.update_one(
        {"user_id": user_key},
        {"$set": {"verified": True}}
    )

    return {
        "success": True,
        "verified": True,
        "message": "Xác thực OTP thành công! Bạn có thể đặt mật khẩu mới ngay bây giờ."
    }


@router.post("/forgot-password/reset")
async def reset_password(payload: ResetPasswordRequest) -> dict:
    db = get_database()
    query_val = payload.email_or_phone.strip()
    otp_val = payload.otp.strip()
    new_pass = payload.new_password.strip()

    if len(new_pass) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự.")

    user = await db.users.find_one({
        "$or": [
            {"email": query_val.lower()},
            {"phone": query_val},
        ]
    })
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản tương ứng.")

    user_key = str(user["_id"])
    matched = False

    # Kiểm tra Redis
    redis = get_redis()
    if redis is not None:
        try:
            stored_otp = await redis.get(f"forgot_otp:{user_key}")
            if stored_otp and stored_otp == otp_val:
                matched = True
        except Exception:
            pass

    # Kiểm tra MongoDB
    if not matched:
        reset_doc = await db.password_resets.find_one({"user_id": user_key})
        if reset_doc and reset_doc.get("otp") == otp_val:
            if reset_doc.get("expires_at") and reset_doc["expires_at"] > datetime.utcnow():
                matched = True

    if not matched:
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc phiên đổi mật khẩu đã hết hạn.")

    # Cập nhật mật khẩu mới cho user
    new_hash = hash_password(new_pass)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}}
    )

    # Xóa OTP sau khi sử dụng thành công
    if redis is not None:
        try:
            await redis.delete(f"forgot_otp:{user_key}")
        except Exception:
            pass
    await db.password_resets.delete_one({"user_id": user_key})

    return {
        "success": True,
        "message": "Đặt lại mật khẩu thành công! Vui lòng đăng nhập bằng mật khẩu mới của bạn."
    }
