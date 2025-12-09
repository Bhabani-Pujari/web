# # auth/router.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db import get_db
# from models import User, UserRole
# from pydantic import BaseModel, EmailStr
# from passlib.context import CryptContext
# from jose import jwt
# import os
# from dotenv import load_dotenv
# from auth.schemas import RegisterRequest, UserRoleEnum


# load_dotenv()
# JWT_SECRET = os.getenv("JWT_SECRET")
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# router = APIRouter(prefix="/auth", tags=["auth"])

# # Pydantic models
# class RegisterRequest(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     role: UserRole

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# # Register endpoint
# @router.post("/register")
# def register(request: RegisterRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_password = pwd_context.hash(request.password)
#     new_user = User(
#         name=request.name,
#         email=request.email,
#         password_hash=hashed_password,
#         role=UserRole(request.role.value)  # <-- important conversion
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "User registered successfully", "user_id": new_user.id}

# # Login endpoint
# @router.post("/login")
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user or not pwd_context.verify(request.password, user.password_hash):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = jwt.encode({"user_id": user.id, "role": user.role.value}, JWT_SECRET, algorithm="HS256")
#     return {"access_token": token, "token_type": "bearer"}





# auth/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.schemas import RegisterRequest, LoginRequest
from auth.utils import get_current_user
from db import get_db
from models import User, UserRole
from passlib.context import CryptContext
from jose import jwt
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm


load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Convert string role to UserRole enum
    role_enum = UserRole.ADMIN if request.role.upper() == "ADMIN" else UserRole.PATIENT
    
    # Hash password
    hashed_password = pwd_context.hash(request.password)
    
    # Create new user
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hashed_password,
        role=role_enum
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return success message with user info
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role.value  # Convert enum to string
        }
    }
# # ------------------------------
# # Register endpoint
# # ------------------------------
# @router.post("/register")
# def register(request: RegisterRequest, db: Session = Depends(get_db)):
#     # Check if email already exists
#     existing_user = db.query(User).filter(User.email == request.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Hash password
#     hashed_password = pwd_context.hash(request.password)

#     # Convert string role to Enum
#     try:
#         role_enum = UserRole(request.role)
#     except ValueError:
#         role_enum = UserRole.PATIENT  # default

#     # Create new user
#     new_user = User(
#         name=request.name,
#         email=request.email,
#         password_hash=hashed_password,
#         role=role_enum
#     )

#     # Add to DB
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {"message": "User registered successfully", "user_id": new_user.id}





# ------------------------------
# Login endpoint
# ------------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 sends 'username' field, but we store email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {"user_id": user.id, "role": user.role.value}, 
        JWT_SECRET, 
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}







# ------------------------------
# Optional: Get current user
# ------------------------------
@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }
