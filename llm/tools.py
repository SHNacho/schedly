from datetime import datetime
from typing import Annotated
from typing import Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph.state import BaseStore
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt import InjectedStore
from langgraph.prebuilt import ToolNode
from sqlalchemy import Date

from db import Session
from db.crud import create_appointment
from db.crud import create_customer
from db.crud import delete_appointment
from db.crud import get_all_appointments
from db.crud import get_all_employees
from db.crud import get_all_schedules
from db.crud import get_all_services
from db.crud import get_customer
from db.crud import get_service
from db.crud import update_appointment
from db.models import Appointment
from db.models import WorkSchedule
from db.schemas import AppointmentCreate
from db.schemas import CustomerCreate
from llm.utils import calculate_available_intervals
from llm.utils import calculate_unavailable_intervals
from llm.utils import time_interval_into_slots


def _employee_available_hours(
    appointment_date: str,
    service_id: int,
    employee_id: int,
) -> str:
    """
    Call to list all available hours for a service and a employee in a date.

    Params:
        appointment_date (date): Appointment date in the format "%Y-%m-%d"
        service_id (int): Identifier of the service for the appointment
        employee_id (int): Identifier Team member the client would like
    """
    appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d")

    if appointment_date < datetime.now():
        return (
            f"The date {appointment_date} is on the past. If the user did not "
            "provide a year, maybe it is the next year."
        )

    weekday = appointment_date.weekday()

    with Session() as session:
        employee_schedule = get_all_schedules(
            session,
            filters=[
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.day_of_week == weekday,
            ],
        )
        employee_appointments = get_all_appointments(
            session,
            filters=[
                Appointment.employee_id == employee_id,
                Appointment.appointment_time.cast(Date) == appointment_date.date(),
            ],
        )

        service_duration = get_service(session, service_id).duration_minutes
        unavailable_intervals = calculate_unavailable_intervals(employee_appointments)
        available_intervals = calculate_available_intervals(
            unavailable_intervals,
            employee_schedule,
        )
        free_slots = []
        for a_interval in available_intervals:
            free_slots.extend(
                time_interval_into_slots(
                    a_interval[0],
                    a_interval[1],
                    service_duration,
                ),
            )

        return free_slots


@tool
def tool_list_services() -> str:
    """
    Call to list all available services and information about them. Useful to check
    which services the business provide.
    """
    db_session = Session()
    services = get_all_services(db_session)
    str_services = "These are the available services:\n"
    for service in services:
        str_services += f"- {str(service)}\n"
    return str_services


@tool
def tool_list_employees() -> str:
    """
    Call to list all employees and information about them. Useful to get the ID of the
    employee to book an appointment or check its available hours.
    """
    with Session() as db_session:
        employees = get_all_employees(db_session)
        str_employees = "These are the employees:\n"
        for employee in employees:
            str_employees += f"- {str(employee)}\n"
    return str_employees


@tool
def tool_available_hours(appointment_date: str, service_id: int) -> str:
    """
    Call to list all available hours for a service in a date.

    Params:
        appointment_date (date): Appointment date in the format "%Y-%m-%d"
        service_id (int): Identifier of the service for the appointment
    """
    session = Session()
    # Get all available slots for the service in the date
    employees = get_all_employees(session)
    str_available_hours = f"Available hours for {appointment_date}:\n"
    for employee in employees:
        str_available_hours += f"{employee.name}:\n"
        employee_available_hours = _employee_available_hours(
            appointment_date,
            service_id,
            employee.id,
        )
        for available_hour in employee_available_hours:
            str_available_hours += f"\t- {available_hour}\n"
    return str_available_hours


@tool
def tool_employee_available_hours(
    appointment_date: str,
    service_id: int,
    employee_id: int,
):
    """
    Call to list all available hours for a service and a employee in a date.

    Params:
        appointment_date (date): Appointment date in the format "%Y-%m-%d"
        service_id (int): Identifier of the service for the appointment
        employee_id (int): Identifier Team member the client would like
    """
    str_free_hours = f"Available hours for {appointment_date}:\n"
    for free_hour in _employee_available_hours(
        appointment_date,
        service_id,
        employee_id,
    ):
        str_free_hours += f"- {free_hour}\n"
    return str_free_hours


@tool
def tool_save_customer(
    customer_id: Annotated[int, InjectedState("customer_id")],
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
):
    """
    Call to save a new customer in the database

    Params:
        name (str): Name of the new customer
        email (str): Optional. Email of the new customer. Default to None
        phone (str): Optional. Phone of the new customer. Default to None
    """
    message = "Customer created successfully"
    customer = CustomerCreate(
        name=name,
        email=email,
        phone=phone,
    )
    with Session() as session:
        create_customer(session, customer)
    return message


@tool
def tool_save_appointment(
    customer_id: Annotated[int, InjectedState("customer_id")],
    employee_id: int,
    service_id: int,
    appointment_datetime: str,
):
    """
    Call to save an appointment in the database.

    Params:
        customer_id (int): Identifier of the customer
        employee_id (int): Identifier of the employee
        service_id (int): Identifier of the service
        appointment_datetime (str): Appointment date and time in the format "%Y-%m-%d %H:%M:%S"
    """
    message = "Appointment saved successfully"
    with Session() as session:
        customer = get_customer(session, customer_id)
        if customer:
            appointment = AppointmentCreate(
                appointment_time=appointment_datetime,
                customer_id=customer_id,
                employee_id=employee_id,
                service_id=service_id,
            )
            create_appointment(session, appointment)
        else:
            message = (
                "The customer does not exists in our database. "
                "Please first get the customer data and save it into "
                "the database, then call this tool again."
            )
    return message


@tool
def tool_list_customer_appointments(
    customer_id: Annotated[int, InjectedState("customer_id")],
):
    """
    Call to list all appointments for the customer.
    """
    with Session() as session:
        appointments = get_all_appointments(
            session,
            filters=[
                Appointment.customer_id == customer_id,
                Appointment.appointment_time >= datetime.now(),
            ],
        )
        str_appointments = "These are your appointments:\n"
        for appointment in appointments:
            str_appointments += f"- {str(appointment)}\n"
    return str_appointments


@tool
def tool_update_appointment(
    appointment_id: int,
    appointment_datetime: str,
    employee_id: int,
    service_id: int,
    customer_id: Annotated[int, InjectedState("customer_id")],
):
    """
    Use to update or change an exisisting appointment for the customer.

    Params:
        appointment_id (int): Identifier of the appointment to be updated.
        appointment_datetime (str): New appointment date and time in the format "%Y-%m-%d %H:%M:%S"
        employee_id (int): Identifier of the employee assigned. Can be the same or a different employee
        service_id (int): Identifier of the service. Can be the same or a different service
    """
    with Session() as session:
        appointment = AppointmentCreate(
            appointment_time=appointment_datetime,
            customer_id=customer_id,
            employee_id=employee_id,
            service_id=service_id,
        )
        constraints = [Appointment.customer_id == customer_id]
        if update_appointment(session, appointment_id, appointment, constraints):
            return "Appointment updated successfully."
        else:
            return "You are not authorized to update this appointment."


@tool
def tool_delete_appointment(
    appointment_id: int,
    customer_id: Annotated[int, InjectedState("customer_id")],
):
    """
    Call to delete an appointment from the database.

    Params:
        appointment_id (int): Identifier of the appointment
    """
    with Session() as session:
        constraints = [Appointment.customer_id == customer_id]
        if delete_appointment(session, appointment_id, constraints):
            return "Appointment deleted successfully."
        else:
            return "You are not authorized to delete this appointment."


if __name__ == "__main__":
    pass
