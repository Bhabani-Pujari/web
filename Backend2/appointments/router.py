from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Appointment, Doctor, User
from auth.utils import get_current_user, admin_required
from appointments.schemas import AppointmentCreate, AppointmentOut
from datetime import datetime, timedelta
from typing import List
import logging

# ✅ Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])

# ========================================
# PATIENT ENDPOINTS
# ========================================

# Book appointment - FIXED
@router.post("/", response_model=AppointmentOut)
async def book_appointment(
    request: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Book an appointment"""
    logger.info(f"Received appointment request: doctor_id={request.doctor_id}, date={request.date}, time={request.time}")
    
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == request.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Parse date and time
    try:
        appointment_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(request.time, "%H:%M").time()
    except ValueError as e:
        logger.error(f"Date/time parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
    # Combine into datetime objects
    start_datetime = datetime.combine(appointment_date, appointment_time)
    end_datetime = start_datetime + timedelta(minutes=doctor.duration_minutes)
    
    # Check if slot is already booked
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == request.doctor_id,
        Appointment.date == appointment_date,
        Appointment.time == appointment_time,
        Appointment.status != "CANCELLED"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    # Create appointment
    new_appointment = Appointment(
        doctor_id=request.doctor_id,
        patient_id=current_user.id,
        date=appointment_date,
        time=appointment_time,
        status="PENDING"
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    logger.info(f"Appointment created successfully: id={new_appointment.id}")
    
    # Return formatted response
    return {
        "id": new_appointment.id,
        "start_at": start_datetime.isoformat(),
        "end_at": end_datetime.isoformat(),
        "status": new_appointment.status,
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty
        },
        "patient": {
            "id": current_user.id,
            "name": current_user.name
        }
    }

# Get my appointments - FIXED
@router.get("/me", response_model=List[AppointmentOut])
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's appointments"""
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == current_user.id
    ).all()
    
    result = []
    for apt in appointments:
        # Combine date and time into datetime
        start_datetime = datetime.combine(apt.date, apt.time)
        
        # Calculate end time using doctor's duration
        duration = apt.doctor.duration_minutes if apt.doctor else 60
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        result.append({
            "id": apt.id,
            "start_at": start_datetime.isoformat(),
            "end_at": end_datetime.isoformat(),
            "status": apt.status,
            "doctor": {
                "id": apt.doctor.id,
                "name": apt.doctor.name,
                "specialty": apt.doctor.specialty
            } if apt.doctor else None,
            "patient": {
                "id": current_user.id,
                "name": current_user.name
            }
        })
    
    return result

# Cancel appointment - FIXED
@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mark as cancelled
    appointment.status = "CANCELLED"
    db.commit()
    
    logger.info(f"Appointment {appointment_id} cancelled by user {current_user.id}")
    
    return {"message": "Appointment cancelled successfully"}

# ========================================
# PUBLIC/DOCTOR ENDPOINTS
# ========================================

# Get doctor's appointments
@router.get("/doctor/{doctor_id}")
async def get_doctor_appointments(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific doctor"""
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status != "CANCELLED"
    ).all()
    
    result = []
    for apt in appointments:
        start_datetime = datetime.combine(apt.date, apt.time)
        duration = apt.doctor.duration_minutes if apt.doctor else 60
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        result.append({
            "id": apt.id,
            "start_at": start_datetime.isoformat(),
            "end_at": end_datetime.isoformat(),
            "status": apt.status
        })
    
    return result

# ========================================
# ADMIN ENDPOINTS
# ========================================

# Get all appointments - ADMIN
@router.get("/all")
async def get_all_appointments(
    current_user = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get all appointments (admin only)"""
    appointments = db.query(Appointment).all()
    
    result = []
    for apt in appointments:
        start_datetime = datetime.combine(apt.date, apt.time)
        duration = apt.doctor.duration_minutes if apt.doctor else 60
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        result.append({
            "id": apt.id,
            "start_at": start_datetime.isoformat(),
            "end_at": end_datetime.isoformat(),
            "status": apt.status,
            "doctor": {
                "id": apt.doctor.id,
                "name": apt.doctor.name,
                "specialty": apt.doctor.specialty
            } if apt.doctor else None,
            "patient": {
                "id": apt.patient.id,
                "name": apt.patient.name
            } if apt.patient else None
        })
    
    return result