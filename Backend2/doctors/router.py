from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Doctor, DoctorSchedule, DayOfWeek
from auth.utils import admin_required
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# ========================================
# Schemas
# ========================================
class DoctorCreate(BaseModel):
    name: str
    email: str
    specialty: str
    bio: Optional[str] = None
    duration_minutes: Optional[int] = 60

class ScheduleCreateRequest(BaseModel):
    weekday: int
    start_time: str
    end_time: str

# ========================================
# Router
# ========================================
router = APIRouter(prefix="/doctors", tags=["doctors"])

# ========================================
# ROUTES (Order matters!)
# ========================================

# 1️⃣ /all MUST be FIRST (before /{doctor_id})
@router.get("/all")
async def get_all_doctors_admin(
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get all doctors - admin"""
    doctors = db.query(Doctor).all()
    
    # Map day enum value to weekday number for frontend
    day_to_weekday = {
        "SUNDAY": 0, "MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3,
        "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6
    }
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "email": d.email,
            "specialty": d.specialty,
            "bio": d.bio,
            "duration_minutes": d.duration_minutes or 60,
            "schedules": [
                {
                    "id": s.id,
                    "weekday": day_to_weekday.get(s.day.value, 0),
                    "start_time": s.start_time.strftime("%H:%M"),
                    "end_time": s.end_time.strftime("%H:%M")
                }
                for s in d.schedules
            ]
        }
        for d in doctors
    ]

# 2️⃣ Get all doctors - PUBLIC
@router.get("/")
async def get_all_doctors_public(db: Session = Depends(get_db)):
    """Get all doctors - public"""
    doctors = db.query(Doctor).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "email": d.email,
            "specialty": d.specialty,
            "bio": d.bio,
            "duration_minutes": d.duration_minutes or 60
        }
        for d in doctors
    ]

# 3️⃣ Create doctor
@router.post("/")
async def create_doctor(
    doctor: DoctorCreate,
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Create doctor"""
    # Check if email exists
    existing = db.query(Doctor).filter(Doctor.email == doctor.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new doctor
    new_doctor = Doctor(
        name=doctor.name,
        email=doctor.email,
        specialty=doctor.specialty,
        bio=doctor.bio,
        duration_minutes=doctor.duration_minutes or 60
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return {
        "id": new_doctor.id,
        "name": new_doctor.name,
        "email": new_doctor.email,
        "specialty": new_doctor.specialty,
        "bio": new_doctor.bio,
        "duration_minutes": new_doctor.duration_minutes
    }

# 4️⃣ Get single doctor (MUST be after /all)
@router.get("/{doctor_id}")
async def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get single doctor with schedules"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get schedules
    schedules = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id).all()
    
    # Map day enum to weekday number
    day_to_weekday = {
        "SUNDAY": 0, "MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3,
        "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6
    }
    
    return {
        "id": doctor.id,
        "name": doctor.name,
        "email": doctor.email,
        "specialty": doctor.specialty,
        "bio": doctor.bio,
        "duration_minutes": doctor.duration_minutes or 60,
        "schedules": [
            {
                "id": s.id,
                "weekday": day_to_weekday.get(s.day.value, 0),
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M")
            }
            for s in schedules
        ]
    }

# 5️⃣ Delete doctor
@router.delete("/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete doctor"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}

# 6️⃣ Add schedule
@router.post("/{doctor_id}/schedule")
async def add_schedule(
    doctor_id: int,
    schedule: ScheduleCreateRequest,
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Add schedule for doctor"""
    # Check doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Map weekday number to enum
    day_mapping = {
        0: DayOfWeek.SUNDAY,
        1: DayOfWeek.MONDAY,
        2: DayOfWeek.TUESDAY,
        3: DayOfWeek.WEDNESDAY,
        4: DayOfWeek.THURSDAY,
        5: DayOfWeek.FRIDAY,
        6: DayOfWeek.SATURDAY
    }
    
    if schedule.weekday not in day_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid weekday: {schedule.weekday}. Use 0-6")
    
    day_enum = day_mapping[schedule.weekday]
    
    # Parse times
    try:
        start = datetime.strptime(schedule.start_time, "%H:%M").time()
        end = datetime.strptime(schedule.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    # Validate end time is after start time
    if end <= start:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Check if schedule already exists for this day
    existing = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.day == day_enum
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Schedule already exists for this day. Delete the existing one first.")
    
    # Create schedule
    new_schedule = DoctorSchedule(
        doctor_id=doctor_id,
        day=day_enum,
        start_time=start,
        end_time=end
    )
    
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    
    return {
        "id": new_schedule.id,
        "doctor_id": new_schedule.doctor_id,
        "weekday": schedule.weekday,
        "start_time": schedule.start_time,
        "end_time": schedule.end_time,
        "message": "Schedule added successfully"
    }

# 7️⃣ Delete schedule
@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete schedule"""
    schedule = db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}