from typing import List
from typing import Optional

from db.models import Appointment
from db.models import Customer
from db.models import Employee
from db.models import Service
from db.models import WorkSchedule
from db.schemas import AppointmentCreate
from db.schemas import AppointmentRead
from db.schemas import CustomerCreate
from db.schemas import CustomerRead
from db.schemas import EmployeeCreate
from db.schemas import EmployeeRead
from db.schemas import ServiceCreate
from db.schemas import ServiceRead
from db.schemas import WorkScheduleCreate
from db.schemas import WorkScheduleRead


# Customer CRUD
def create_customer(db_session, customer_data: CustomerCreate):
    customer = Customer(**customer_data.model_dump())
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return CustomerRead.model_validate(customer)


def get_customer(db_session, customer_id: int):
    customer = db_session.query(Customer).filter(Customer.id == customer_id).first()
    return CustomerRead.model_validate(customer) if customer else None


def get_customers(db_session, filters: Optional[List]) -> List[Customer]:
    query = db_session.query(Customer)

    if filters:
        query = query.filter(*filters)

    customers = query.all()
    return [CustomerRead.model_validate(customer) for customer in customers]


def get_telegram_customer(db_session, telegram_name: str):
    customer = (
        db_session.query(Customer)
        .filter(Customer.telegram_name == telegram_name)
        .first()
    )
    return CustomerRead.model_validate(customer) if customer else None


def update_customer(db_session, customer_id: int, customer_data: CustomerCreate):
    customer = db_session.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        for key, value in customer_data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        db_session.commit()
        db_session.refresh(customer)
    return CustomerRead.model_validate(customer) if customer else None


def delete_customer(db_session, customer_id: int):
    customer = db_session.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db_session.delete(customer)
        db_session.commit()
    return customer_id if customer else None


# Employee CRUD
def create_employee(db_session, employee_data: EmployeeCreate):
    employee = Employee(**employee_data.model_dump())
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return EmployeeRead.model_validate(employee)


def get_employee(db_session, employee_id: int):
    employee = db_session.query(Employee).filter(Employee.id == employee_id).first()
    return EmployeeRead.model_validate(employee) if employee else None


def update_employee(db_session, employee_id: int, employee_data: EmployeeCreate):
    employee = db_session.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        for key, value in employee_data.model_dump(exclude_unset=True).items():
            setattr(employee, key, value)
        db_session.commit()
        db_session.refresh(employee)
    return EmployeeRead.model_validate(employee) if employee else None


def delete_employee(db_session, employee_id: int):
    employee = db_session.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        db_session.delete(employee)
        db_session.commit()
    return employee_id if employee else None


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
        db_session.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
    )
    return WorkScheduleRead.model_validate(schedule) if schedule else None


def update_work_schedule(
    db_session,
    schedule_id: int,
    schedule_data: WorkScheduleCreate,
):
    schedule = (
        db_session.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
    )
    if schedule:
        for key, value in schedule_data.model_dump(exclude_unset=True).items():
            setattr(schedule, key, value)
        db_session.commit()
        db_session.refresh(schedule)
    return WorkScheduleRead.model_validate(schedule) if schedule else None


def delete_work_schedule(db_session, schedule_id: int):
    schedule = (
        db_session.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
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
        db_session.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    return AppointmentRead.model_validate(appointment) if appointment else None


def update_appointment(
    db_session,
    appointment_id: int,
    appointment_data: AppointmentCreate,
    filters: Optional[list] = None,
):
    query_filters = [Appointment.id == appointment_id]
    query = db_session.query(Appointment).filter(Appointment.id == appointment_id)

    if filters:
        query_filters.extend(filters)
    appointment = query.filter(*query_filters).first()

    if appointment:
        for key, value in appointment_data.model_dump(exclude_unset=True).items():
            setattr(appointment, key, value)
        db_session.commit()
        db_session.refresh(appointment)

    return AppointmentRead.model_validate(appointment) if appointment else None


def delete_appointment(
    db_session,
    appointment_id: int,
    filters: Optional[list] = None,
):
    query_filters = [Appointment.id == appointment_id]
    query = db_session.query(Appointment)

    if filters:
        query_filters.extend(filters)
    appointment = query.filter(*query_filters).first()

    if appointment:
        db_session.delete(appointment)
        db_session.commit()

    return appointment_id if appointment else None


# Employee: Get all employees with their work schedules and appointments
def get_all_employees(db_session) -> List[EmployeeRead]:
    employees = db_session.query(Employee).all()
    return [EmployeeRead.model_validate(employee) for employee in employees]


def get_all_services(db_session) -> List[ServiceRead]:
    services = db_session.query(Service).all()
    return [ServiceRead.model_validate(service) for service in services]


def get_all_customers(db_session) -> List[CustomerRead]:
    customers = db_session.query(Customer).all()
    return [CustomerRead.model_validate(customer) for customer in customers]


def get_all_appointments(db_session, filters: list = None):  # -> List[AppointmentRead]:
    query = db_session.query(Appointment)
    if filters:
        query = query.filter(*filters)
    appointments = query.all()
    return [AppointmentRead.model_validate(appointment) for appointment in appointments]


def get_all_schedules(db_session, filters: list = None) -> List[WorkScheduleRead]:
    query = db_session.query(WorkSchedule)
    if filters:
        query = query.filter(*filters)
    schedules = query.all()
    return [WorkScheduleRead.model_validate(schedule) for schedule in schedules]


if __name__ == "__main__":
    from db import Session

    print(get_all_employees(Session()))
