from pydantic import BaseModel
from typing import Optional

class DoctorInfo(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None

    class Config:
        from_attributes = True

class PatientInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AppointmentOut(BaseModel):
    id: int
    start_at: str  # ISO datetime string
    end_at: str    # ISO datetime string
    status: str
    doctor: DoctorInfo
    patient: PatientInfo

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    doctor_id: int
    date: str   # "YYYY-MM-DD"
    time: str   # "HH:MM"