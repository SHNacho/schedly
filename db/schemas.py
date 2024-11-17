from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime, time

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

# Appointment Pydantic model
class AppointmentCreate(BaseModel):
    appointment_time: datetime
    customer_id: int
    stylist_id: int
    service_id: int

class AppointmentRead(AppointmentCreate):
    model_config = ConfigDict(from_attributes = True)
    id: int

