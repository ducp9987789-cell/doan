import random
from datetime import datetime, timedelta
from typing import Any, Optional

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ReturnDocument

from app.core.security import create_access_token, hash_password, verify_password
from app.core.utils import serialize_doc, to_object_id
from app.db.mongodb import get_database
from app.db.redis import get_redis
from app.schemas.user import (
    AdminUserCreate,
    AdminUserUpdate,
    ChangePasswordRequest,
    RegisterSendOtpRequest,
    RegisterVerifyOtpRequest,
    ResetPasswordRequest,
    SendOtpRequest,
    UserRegister,
    UserUpdate,
    VerifyOtpRequest,
)
from app.services.email_service import EmailService


class UserService:
    """Service xử lý toàn bộ logic nghiệp vụ liên quan đến Người dùng, Xác thực & OTP."""

    @staticmethod
    async def send_register_otp(payload: RegisterSendOtpRequest) -> dict[str, Any]:
        """Gửi mã OTP 6 số qua email khi người dùng đăng ký tài khoản (hiệu lực 1 phút)."""
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
                detail=f"Không thể gửi mã OTP tới email {email}. Chi tiết lỗi: {err_msg}. Vui lòng kiểm tra cấu hình SMTP trong backend/.env!",
            )

        return {
            "success": True,
            "message": f"Mã xác thực OTP đã được gửi vào hộp thư Gmail của bạn ({email}). Vui lòng kiểm tra email để lấy mã xác nhận!",
        }

    @staticmethod
    async def verify_register_otp(payload: RegisterVerifyOtpRequest) -> dict[str, Any]:
        """Xác thực mã OTP đăng ký trước khi tạo tài khoản."""
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
                detail="Mã OTP không chính xác hoặc đã hết hạn hiệu lực (1 phút). Vui lòng nhấn gửi lại mã mới!",
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

    @staticmethod
    async def register(payload: UserRegister) -> dict[str, Any]:
        """Đăng ký tài khoản người dùng mới (yêu cầu mã OTP hợp lệ)."""
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

    @staticmethod
    async def authenticate(email: str, password: str) -> dict[str, Any]:
        """Xác thực tài khoản và trả về thông tin user."""
        db = get_database()
        user = await db.users.find_one({"email": email.lower().strip()})
        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is disabled")
        return user

    @staticmethod
    async def login(username: str, password: str) -> dict[str, Any]:
        """Đăng nhập và tạo JWT token."""
        user = await UserService.authenticate(username, password)
        token = create_access_token(str(user["_id"]), extra={"role": user["role"]})
        user_data = serialize_doc(user)
        return {"access_token": token, "token_type": "bearer", "user": user_data}

    @staticmethod
    async def get_by_id(user_id: str) -> dict[str, Any]:
        """Lấy thông tin người dùng theo ID."""
        db = get_database()
        user = await db.users.find_one({"_id": to_object_id(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return serialize_doc(user)

    @staticmethod
    async def update_profile(user_id: str, payload: UserUpdate) -> dict[str, Any]:
        """Cập nhật thông tin cá nhân của người dùng."""
        db = get_database()
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if "email" in updates and updates["email"]:
            updates["email"] = updates["email"].lower()
            existing = await db.users.find_one({
                "email": updates["email"],
                "_id": {"$ne": to_object_id(user_id)},
            })
            if existing:
                raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi tài khoản khác")

        updates["updated_at"] = datetime.utcnow()
        result = await db.users.find_one_and_update(
            {"_id": to_object_id(user_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return serialize_doc(result)

    @staticmethod
    async def change_password(user_id: str, payload: ChangePasswordRequest) -> dict[str, Any]:
        """Đổi mật khẩu người dùng."""
        db = get_database()
        user = await db.users.find_one({"_id": to_object_id(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin người dùng")

        if not verify_password(payload.current_password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác")

        new_hash = hash_password(payload.new_password)
        await db.users.update_one(
            {"_id": to_object_id(user_id)},
            {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}},
        )
        return {"message": "Đổi mật khẩu thành công! Vui lòng ghi nhớ mật khẩu mới."}

    @staticmethod
    async def send_forgot_otp(payload: SendOtpRequest) -> dict[str, Any]:
        """Gửi mã OTP khôi phục mật khẩu."""
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
                detail="Không tìm thấy tài khoản nào khớp với email hoặc số điện thoại này.",
            )

        otp = str(random.randint(100000, 999999))
        user_key = str(user["_id"])
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        redis = get_redis()
        if redis is not None:
            try:
                await redis.setex(f"forgot_otp:{user_key}", 300, otp)
            except Exception:
                pass

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
                detail="Tài khoản này chưa có thông tin email để nhận mã OTP.",
            )

        email_res = EmailService.send_otp_email(to_email=user["email"], otp=otp, purpose="forgot")
        if not email_res.get("success", False):
            err_msg = email_res.get("error") or "Không thể gửi email OTP."
            raise HTTPException(
                status_code=500,
                detail=f"Không thể gửi mã OTP tới email {user['email']}. Chi tiết lỗi: {err_msg}. Vui lòng kiểm tra cấu hình SMTP trong backend/.env!",
            )

        return {
            "success": True,
            "message": f"Mã xác thực OTP đã được gửi đến email {user['email']}. Vui lòng kiểm tra hộp thư của bạn!",
            "email_or_phone": query_val,
        }

    @staticmethod
    async def verify_forgot_otp(payload: VerifyOtpRequest) -> dict[str, Any]:
        """Xác thực mã OTP khôi phục mật khẩu."""
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

        redis = get_redis()
        if redis is not None:
            try:
                stored_otp = await redis.get(f"forgot_otp:{user_key}")
                if stored_otp and stored_otp == otp_val:
                    matched = True
            except Exception:
                pass

        if not matched:
            reset_doc = await db.password_resets.find_one({"user_id": user_key})
            if reset_doc and reset_doc.get("otp") == otp_val:
                if reset_doc.get("expires_at") and reset_doc["expires_at"] > datetime.utcnow():
                    matched = True

        if not matched:
            raise HTTPException(status_code=400, detail="Mã OTP không chính xác hoặc đã hết hạn.")

        await db.password_resets.update_one(
            {"user_id": user_key},
            {"$set": {"verified": True}},
        )

        return {
            "success": True,
            "verified": True,
            "message": "Xác thực OTP thành công! Bạn có thể đặt mật khẩu mới ngay bây giờ.",
        }

    @staticmethod
    async def reset_password(payload: ResetPasswordRequest) -> dict[str, Any]:
        """Đặt lại mật khẩu sau khi xác thực OTP."""
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

        redis = get_redis()
        if redis is not None:
            try:
                stored_otp = await redis.get(f"forgot_otp:{user_key}")
                if stored_otp and stored_otp == otp_val:
                    matched = True
            except Exception:
                pass

        if not matched:
            reset_doc = await db.password_resets.find_one({"user_id": user_key})
            if reset_doc and reset_doc.get("otp") == otp_val:
                if reset_doc.get("expires_at") and reset_doc["expires_at"] > datetime.utcnow():
                    matched = True

        if not matched:
            raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc phiên đổi mật khẩu đã hết hạn.")

        new_hash = hash_password(new_pass)
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}},
        )

        if redis is not None:
            try:
                await redis.delete(f"forgot_otp:{user_key}")
            except Exception:
                pass
        await db.password_resets.delete_one({"user_id": user_key})

        return {
            "success": True,
            "message": "Đặt lại mật khẩu thành công! Vui lòng đăng nhập bằng mật khẩu mới của bạn.",
        }

    @staticmethod
    async def list_users() -> list[dict[str, Any]]:
        """Lấy danh sách toàn bộ người dùng cho Admin."""
        db = get_database()
        cursor = db.users.find({}).sort("created_at", -1)
        return [serialize_doc(doc) for doc in await cursor.to_list(length=500)]

    @staticmethod
    async def admin_create_user(payload: AdminUserCreate) -> dict[str, Any]:
        """Admin tạo tài khoản người dùng mới."""
        if payload.role not in {"customer", "admin"}:
            raise HTTPException(status_code=400, detail="Invalid role")
        db = get_database()
        existing = await db.users.find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        doc = {
            "email": payload.email.lower(),
            "full_name": payload.full_name,
            "hashed_password": hash_password(payload.password),
            "role": payload.role,
            "phone": payload.phone,
            "address": None,
            "is_active": payload.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize_doc(doc)

    @staticmethod
    async def admin_update_user(
        user_id: str,
        payload: AdminUserUpdate,
        current_admin_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Admin cập nhật thông tin / trạng thái / vai trò của người dùng."""
        if payload.role is not None and payload.role not in {"customer", "admin"}:
            raise HTTPException(status_code=400, detail="Invalid role")

        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k != "password"}
        if payload.password:
            updates["hashed_password"] = hash_password(payload.password)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Ngăn chặn admin tự khóa tài khoản hoặc tự hạ quyền chính mình
        if current_admin_id and str(current_admin_id) == str(user_id):
            if updates.get("is_active") is False:
                raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
            if updates.get("role") == "customer":
                raise HTTPException(status_code=400, detail="Cannot remove admin role from your own account")

        updates["updated_at"] = datetime.utcnow()
        db = get_database()
        result = await db.users.find_one_and_update(
            {"_id": to_object_id(user_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return serialize_doc(result)

