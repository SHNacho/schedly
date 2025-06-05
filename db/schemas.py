from datetime import datetime
from datetime import time
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr

from db.enum import Weekday


# Pydantic models for data validation
# Customer Pydantic model
class CustomerCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    telegram_name: Optional[str] = None


class CustomerRead(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    appointments: Optional[List["AppointmentRead"]] = None


# Employee Pydantic model
class EmployeeCreate(BaseModel):
    name: str
    specialty: Optional[str] = None


class EmployeeRead(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    work_schedules: Optional[List["WorkScheduleRead"]] = None
    appointments: Optional[List["AppointmentRead"]] = None

    def __str__(self):
        result = f"ID: {self.id}; Name: {self.name}"
        return result


# Service Pydantic model
class ServiceCreate(BaseModel):
    name: str
    price: float
    duration_minutes: int


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

    def __str__(self):
        result = f"ID: {self.id}; Name: {self.name}; Price: {self.price} EUR; Duration: {self.duration_minutes} minutes"
        return result


# WorkSchedule Pydantic model
class WorkScheduleCreate(BaseModel):
    employee_id: int
    day_of_week: int  # 0=Monday, 1=Tuesday, etc.
    start_time: time
    end_time: time


class WorkScheduleRead(WorkScheduleCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

    def __str__(self):
        result = f"{Weekday(self.day_of_week).name}: from {time.strftime(self.start_time, '%H:%M:%S')} to {time.strftime(self.end_time, '%H:%M:%S')}"
        return result


# Appointment Pydantic model
class AppointmentCreate(BaseModel):
    appointment_time: datetime
    customer_id: int
    employee_id: int
    service_id: int


class AppointmentRead(AppointmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

    # customer: Optional[CustomerRead] = None
    # employee: Optional[EmployeeRead] = None
    service: Optional[ServiceRead] = None

    def __str__(self):
        result = f"ID: {self.id}; Employee ID: {self.employee_id}; Service ID: {self.service}; Date and Time: {datetime.strftime(self.appointment_time, '%A, %d-%m-%Y %H:%M:%S')}"
        return result
