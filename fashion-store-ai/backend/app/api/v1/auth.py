from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.core.utils import serialize_doc
from app.db.mongodb import get_database
from app.schemas.user import TokenResponse, UserRegister, UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister) -> dict:
    db = get_database()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": payload.email.lower(),
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
    from bson import ObjectId
    from pymongo import ReturnDocument

    db = get_database()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    updates["updated_at"] = datetime.utcnow()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(current_user["id"])},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_doc(result)
