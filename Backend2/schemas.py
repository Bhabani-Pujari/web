from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import RoleEnum, AppointmentStatus


# User
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum
    class Config:
        orm_mode = True

# Doctor
class DoctorCreate(BaseModel):
    name: str
    specialty: str
    bio: Optional[str] = None
    duration_minutes: int

class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str
    bio: Optional[str] = None
    duration_minutes: int
    class Config:
        orm_mode = True

# Appointment
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_at: datetime
    end_at: datetime

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    class Config:
        orm_mode = True


