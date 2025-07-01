from datetime import datetime
from datetime import time
from typing import Any
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Json

from db.enum import Weekday


# Pydantic models for data validation

# TODO: create schemas for Business


# Business Pydantic model
class BusinessCreate(BaseModel):
    name: str
    google_credentials: Optional[dict] = None


class BusinessRead(BusinessCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employees: Optional[List["EmployeeRead"]]


# Customer Pydantic model
class CustomerCreate(BaseModel):
    business_id: int
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
    business_id: int


class EmployeeRead(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    google_calendar_id: Optional[str]
    work_schedules: Optional[List["WorkScheduleRead"]] = None
    appointments: Optional[List["AppointmentRead"]] = None

    def __str__(self):
        result = f"ID: {self.id}; Name: {self.name}"
        return result


# Service Pydantic model
class ServiceCreate(BaseModel):
    business_id: int
    name: str
    price: float
    duration_minutes: int


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

    def __str__(self):
        result = (
            f"ID: {self.id}; Name: {self.name}; "
            f"Price: {self.price} EUR; "
            f"Duration: {self.duration_minutes} minutes"
        )
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
        result = (
            f"{Weekday(self.day_of_week).name}: "
            f"from {time.strftime(self.start_time, '%H:%M:%S')} "
            f"to {time.strftime(self.end_time, '%H:%M:%S')}"
        )
        return result


# Appointment Pydantic model
class AppointmentCreate(BaseModel):
    appointment_time: datetime
    customer_id: int
    employee_id: int
    service_id: int
    google_calendar_id: Optional[str] = None


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    appointment_time: datetime
    employee_service_id: int
    google_calendar_id: Optional[str] = None

    # customer: Optional[CustomerRead] = None
    employee: Optional[EmployeeRead] = None
    service: Optional[ServiceRead] = None

    def __str__(self):
        result = (
            f"ID: {self.id}; Employee ID: {self.employee.id}; "
            f"Service ID: {self.service}; "
            f"Date and Time: {datetime.strftime(self.appointment_time, '%A, %d-%m-%Y %H:%M:%S')}"
        )
        return result
