# # auth/schemas.py
# # from pydantic import BaseModel, EmailStr
# # from enum import Enum

# # class UserRoleEnum(str, Enum):
# #     ADMIN = "ADMIN"
# #     PATIENT = "PATIENT"

# # class RegisterRequest(BaseModel):
# #     name: str
# #     email: EmailStr
# #     password: str
# #     role: UserRoleEnum
    
    
    
# from pydantic import BaseModel, EmailStr
# from models import UserRole

# class RegisterRequest(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     role: UserRole

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str
    
    
# class UserCreate(BaseModel):
#     name: str
#     email: str
#     password: str
#     role: str = "PATIENT"
    
    
    
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "PATIENT"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True
    
    
    
    
    
    

