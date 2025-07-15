from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from config import load_config

config = load_config()
# Initialize the base and engine
Base = declarative_base()


# Business model
class Business(Base):
    __tablename__ = "business"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    google_credentials = Column(JSON)

    employees = relationship("Employee", back_populates="business")


# Telegram Bot model
class TelegramBot(Base):
    __tablename__ = "telegram_bots"
    id = Column(Integer, primary_key=True)
    telegram_username = Column(String, unique=True, index=True)
    token = Column(String, unique=True)
    business_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )


# WhatsApp Bot model
class WhatsappBot(Base):
    __tablename__ = "whatsapp_bots"
    id = Column(Integer, primary_key=True)
    waba_id = Column(String, unique=True, index=True)
    token = Column(String, unique=True)
    business_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )


# Customer model
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    telegram_name = Column(String, nullable=True, index=True)
    whatsapp_id = Column(String, nullable=True, index=True)

    appointments = relationship("Appointment", back_populates="customer")


# Employee model
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    google_calendar_id = Column(String, unique=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    business = relationship("Business", back_populates="employees")
    work_schedules = relationship("WorkSchedule", back_populates="employee")
    services = relationship(
        "Service",
        secondary="employee_services",
        back_populates="employees",
    )

    # employee_services = relationship("EmployeeServices", back_populates="employee")


# Service model
class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    employees = relationship(
        "Employee",
        secondary="employee_services",
        back_populates="services",
    )
    # employee_services = relationship(
    #    "EmployeeServices",
    #    back_populates="service",
    # )


# Relationship between Services and Employees
class EmployeeServices(Base):
    __tablename__ = "employee_services"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )

    employee = relationship("Employee", viewonly=True)
    service = relationship("Service", viewonly=True)


# WorkSchedule model
class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    employee = relationship("Employee", back_populates="work_schedules")


# Appointment model
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    appointment_time = Column(DateTime, default=datetime.now(timezone.utc))
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_service_id = Column(
        Integer,
        ForeignKey("employee_services.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    google_calendar_id = Column(String)

    customer = relationship("Customer", back_populates="appointments")
    employee_service = relationship("EmployeeServices")

    @property
    def employee(self):
        return self.employee_service.employee

    @property
    def service(self):
        return self.employee_service.service
