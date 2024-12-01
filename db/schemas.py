from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime, time

from db.enum import Weekday

# Pydantic models for data validation

# Customer Pydantic model
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class CustomerRead(CustomerCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int
    appointments: Optional[List["AppointmentRead"]] = None

# Stylist Pydantic model
class StylistCreate(BaseModel):
    name: str
    specialty: Optional[str] = None

class StylistRead(StylistCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int
    work_schedules: Optional[List["WorkScheduleRead"]] = None
    appointments: Optional[List["AppointmentRead"]] = None

    def __str__(self):
        result = (
            f"Name: {self.name}\n"
            f"Specialty: {self.specialty}\n"
        )
        if self.work_schedules:
            result += "Work Schedules:\n"
            for ws in self.work_schedules:
                result += f"  - {str(ws)}\n"
        if self.appointments:
            result += "Appointments:\n"
            for a in self.appointments:
                result += f"  - {str(a)}\n"
        return result

# Service Pydantic model
class ServiceCreate(BaseModel):
    name: str
    price: float
    duration_minutes: int

class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int

# WorkSchedule Pydantic model
class WorkScheduleCreate(BaseModel):
    stylist_id: int
    day_of_week: int  # 0=Monday, 1=Tuesday, etc.
    start_time: time
    end_time: time

class WorkScheduleRead(WorkScheduleCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int

    def __str__(self):
        result = (
            f"{Weekday(self.day_of_week).name}: from {time.strftime(self.start_time, '%H:%M:%S')} to {time.strftime(self.end_time, '%H:%M:%S')}"
        )
        return result

# Appointment Pydantic model
class AppointmentCreate(BaseModel):
    appointment_time: datetime
    customer_id: int
    stylist_id: int
    service_id: int

class AppointmentRead(AppointmentCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int

    def __str__(self):
        result = f"At {datetime.strftime(self.appointment_time, '%d-%m-%Y %H:%M:%S')}"
        return result

