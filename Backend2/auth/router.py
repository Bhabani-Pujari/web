# auth/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.schemas import RegisterRequest, LoginRequest
from auth.utils import get_current_user, hash_password, verify_password  # ← ADD THESE
from db import get_db
from models import User, UserRole
from jose import jwt
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    role_enum = UserRole.ADMIN if request.role.upper() == "ADMIN" else UserRole.PATIENT
    
    hashed_password = hash_password(request.password)  # ← FIXED
    
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hashed_password,
        role=role_enum
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role.value
        }
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):  # ← FIXED
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {"user_id": user.id, "role": user.role.value}, 
        JWT_SECRET, 
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }