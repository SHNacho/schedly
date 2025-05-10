from datetime import datetime
from datetime import timezone

from config import load_config
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

config = load_config()
# Initialize the base and engine
Base = declarative_base()


# Customer model
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    telegram_name = Column(String, unique=True, nullable=True, index=True)

    appointments = relationship("Appointment", back_populates="customer")


# Stylist model
class Stylist(Base):
    __tablename__ = "stylists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    appointments = relationship("Appointment", back_populates="stylist")
    work_schedules = relationship("WorkSchedule", back_populates="stylist")
    services = relationship(
        "Service",
        secondary="stylist_services",
        back_populates="stylists",
    )


# Service model
class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    appointments = relationship("Appointment", back_populates="service")
    stylists = relationship(
        "Stylist",
        secondary="stylist_services",
        back_populates="services",
    )


# Relationship between Services and Stylists
class StylistServices(Base):
    __tablename__ = "stylist_services"
    stylist_id = Column(Integer, ForeignKey("stylists.id"), primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), primary_key=True)


# WorkSchedule model
class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    id = Column(Integer, primary_key=True)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    stylist = relationship("Stylist", back_populates="work_schedules")


# Appointment model
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    appointment_time = Column(DateTime, default=datetime.now(timezone.utc))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    customer = relationship("Customer", back_populates="appointments")
    stylist = relationship("Stylist", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
