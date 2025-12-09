from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Time, Date, Text
from sqlalchemy.orm import relationship
from db import Base
import enum

# ------------------------------
# Roles for users
# ------------------------------
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    PATIENT = "PATIENT"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.PATIENT)

    appointments = relationship("Appointment", back_populates="patient")


# ------------------------------
# Days of the week
# ------------------------------
class DayOfWeek(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


# ------------------------------
# Doctors
# ------------------------------
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    specialty = Column(String(100))
    bio = Column(Text)
    duration_minutes = Column(Integer, default=60)

    schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete")

    
# ------------------------------
# Doctor schedules
# ------------------------------
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    day = Column(Enum(DayOfWeek))
    start_time = Column(Time)
    end_time = Column(Time)

    doctor = relationship("Doctor", back_populates="schedules")


# ------------------------------
# Appointments
# ------------------------------
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date)
    time = Column(Time)
    status = Column(String(20), default="PENDING")

    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("User", back_populates="appointments")