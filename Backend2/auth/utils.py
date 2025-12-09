# # auth/utils.py
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from jose import jwt
# import os
# from dotenv import load_dotenv

# load_dotenv()

# JWT_SECRET = os.getenv("JWT_SECRET")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     token = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
#     return token



from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from db import get_db
from models import User, UserRole

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

# ✅ CRITICAL: tokenUrl must match your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError as e:
        print(f"JWT Error: {e}")  # ✅ Add logging
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user


def admin_required(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user