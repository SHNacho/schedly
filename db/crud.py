from typing import List
from db.models import (
    Customer,
    Stylist,
    WorkSchedule,
    Appointment,
    Service
)
from db.schemas import(
    CustomerCreate, CustomerRead,
    StylistCreate, StylistRead,
    WorkScheduleCreate, WorkScheduleRead,
    AppointmentCreate, AppointmentRead,
    ServiceCreate, ServiceRead
)

# Customer CRUD
def create_customer(db_session, customer_data: CustomerCreate):
    customer = Customer(**customer_data.model_dump())
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return CustomerRead.model_validate(customer)

def get_customer(db_session, customer_id: int):
    customer = (
        db_session.query(Customer)
        .outerjoin(Appointment)
        .filter(Customer.id == customer_id)
        .first()
    )
    return CustomerRead.model_validate(customer) if customer else None

def update_customer(db_session, customer_id: int, customer_data: CustomerCreate):
    customer = (
        db_session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )
    if customer:
        for key, value in customer_data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        db_session.commit()
        db_session.refresh(customer)
    return CustomerRead.model_validate(customer) if customer else None

def delete_customer(db_session, customer_id: int):
    customer = (
        db_session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )
    if customer:
        db_session.delete(customer)
        db_session.commit()
    return customer_id if customer else None

# Stylist CRUD
def create_stylist(db_session, stylist_data: StylistCreate):
    stylist = Stylist(**stylist_data.model_dump())
    db_session.add(stylist)
    db_session.commit()
    db_session.refresh(stylist)
    return StylistRead.model_validate(stylist)

def get_stylist(db_session, stylist_id: int):
    stylist = (
        db_session.query(Stylist)
        .filter(Stylist.id == stylist_id)
        .first()
    )
    return StylistRead.model_validate(stylist) if stylist else None

def update_stylist(db_session, stylist_id: int, stylist_data: StylistCreate):
    stylist = db_session.query(Stylist).filter(Stylist.id == stylist_id).first()
    if stylist:
        for key, value in stylist_data.model_dump(exclude_unset=True).items():
            setattr(stylist, key, value)
        db_session.commit()
        db_session.refresh(stylist)
    return StylistRead.model_validate(stylist) if stylist else None

def delete_stylist(db_session, stylist_id: int):
    stylist = db_session.query(Stylist).filter(Stylist.id == stylist_id).first()
    if stylist:
        db_session.delete(stylist)
        db_session.commit()
    return stylist_id if stylist else None

# Service CRUD
def create_service(db_session, service_data: ServiceCreate):
    service = Service(**service_data.model_dump())
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return ServiceRead.model_validate(service)

def get_service(db_session, service_id: int):
    service = db_session.query(Service).filter(Service.id == service_id).first()
    return ServiceRead.model_validate(service) if service else None

def update_service(db_session, service_id: int, service_data: ServiceCreate):
    service = db_session.query(Service).filter(Service.id == service_id).first()
    if service:
        for key, value in service_data.model_dump(exclude_unset=True).items():
            setattr(service, key, value)
        db_session.commit()
        db_session.refresh(service)
    return ServiceRead.model_validate(service) if service else None

def delete_service(db_session, service_id: int):
    service = db_session.query(Service).filter(Service.id == service_id).first()
    if service:
        db_session.delete(service)
        db_session.commit()
    return service_id if service else None

# WorkSchedule CRUD
def create_work_schedule(db_session, schedule_data: WorkScheduleCreate):
    schedule = WorkSchedule(**schedule_data.model_dump())
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    return WorkScheduleRead.model_validate(schedule)

def get_work_schedule(db_session, schedule_id: int):
    schedule = (
        db_session.query(WorkSchedule)
        .filter(WorkSchedule.id == schedule_id)
        .first()
    )
    return WorkScheduleRead.model_validate(schedule) if schedule else None

def update_work_schedule(
        db_session, 
        schedule_id: int, 
        schedule_data: WorkScheduleCreate
):
    schedule = (
        db_session.query(WorkSchedule)
        .filter(WorkSchedule.id == schedule_id)
        .first()
    )
    if schedule:
        for key, value in schedule_data.model_dump(exclude_unset=True).items():
            setattr(schedule, key, value)
        db_session.commit()
        db_session.refresh(schedule)
    return WorkScheduleRead.model_validate(schedule) if schedule else None

def delete_work_schedule(db_session, schedule_id: int):
    schedule = (
        db_session.query(WorkSchedule)
        .filter(WorkSchedule.id == schedule_id)
        .first()
    )
    if schedule:
        db_session.delete(schedule)
        db_session.commit()
    return schedule_id if schedule else None

# Appointment CRUD
def create_appointment(db_session, appointment_data: AppointmentCreate):
    appointment = Appointment(**appointment_data.model_dump())
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return AppointmentRead.model_validate(appointment)

def get_appointment(db_session, appointment_id: int):
    appointment = (
        db_session.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    return AppointmentRead.model_validate(appointment) if appointment else None

def update_appointment(
        db_session, 
        appointment_id: int, 
        appointment_data: AppointmentCreate
):
    appointment = (
        db_session.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if appointment:
        for key, value in appointment_data.model_dump(exclude_unset=True).items():
            setattr(appointment, key, value)
        db_session.commit()
        db_session.refresh(appointment)
    return AppointmentRead.model_validate(appointment) if appointment else None

def delete_appointment(db_session, appointment_id: int):
    appointment = (
        db_session.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if appointment:
        db_session.delete(appointment)
        db_session.commit()
    return appointment_id if appointment else None

# Stylist: Get all stylists with their work schedules and appointments
def get_all_stylists(db_session) -> List[StylistRead]:
    stylists = (
        db_session.query(Stylist)
        .outerjoin(WorkSchedule)
        .outerjoin(Appointment)
        .all()
    )
    return [StylistRead.model_validate(stylist) for stylist in stylists]

def get_all_services(db_session) -> List[ServiceRead]:
    services = db_session.query(Service).all()
    return [Service.model_validate(service) for service in services]

def get_all_customers(db_session) -> List[CustomerRead]:
    customers = (
        db_session.query(Customer)
        .ourterjoin(Appointment)
        .all
    )
    return [CustomerRead.model_validate(customer) for customer in customers]
