# from pydantic import BaseModel
# from typing import Optional
# from appointments.schemas import AppointmentOut
# from models import DayOfWeek

# # -------------------------------
# # Doctor creation (admin only)
# # -------------------------------
# class DoctorCreate(BaseModel):
#     name: str
#     email: str
#     specialty: str

# # -------------------------------
# # Doctor schedule creation
# # -------------------------------
# class ScheduleCreate(BaseModel):
#     day: DayOfWeek         # must match the DayOfWeek enum: MONDAY, TUESDAY, etc.
#     start_time: str        # "HH:MM"
#     end_time: str          # "HH:MM"

from pydantic import BaseModel, EmailStr
from typing import Optional
from models import DayOfWeek

class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    specialty: str
    bio: Optional[str] = None  # ✅ Add this line
    


class ScheduleCreate(BaseModel):
    day: str  # "MONDAY"
    start_time: str  # "13:00"
    end_time: str    # "15:00"

class AppointmentCreate(BaseModel):
    doctor_id: int
    day: str        # "THURSDAY"
    time: str       # "13:30"