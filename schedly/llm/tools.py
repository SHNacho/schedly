from datetime import datetime

from db import Session
from db.crud import create_appointment
from db.crud import delete_appointment
from db.crud import get_all_appointments
from db.crud import get_all_schedules
from db.crud import get_all_services
from db.crud import get_all_stylists
from db.crud import get_service
from db.crud import update_appointment
from db.models import Appointment
from db.models import WorkSchedule
from db.schemas import AppointmentCreate
from langchain_core.tools import tool
from llm.utils import calculate_available_intervals
from llm.utils import calculate_unavailable_intervals
from llm.utils import time_interval_into_slots
from sqlalchemy import Date
from sqlalchemy import func


def _stylist_available_hours(
    appointment_date: str,
    service_id: int,
    stylist_id: int,
) -> str:
    """
    Call to list all available hours for a service and a stylist in a date.

    Params:
        appointment_date (date): Appointment date in the format "%Y-%m-%d"
        service_id (int): Identifier of the service for the appointment
        stylist_id (int): Identifier Team member the client would like
    """
    appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d")

    if appointment_date < datetime.now():
        return (
            f"The date {appointment_date} is on the past. If the user did not "
            "provide a year, maybe it is the next year."
        )

    weekday = appointment_date.weekday()

    with Session() as session:
        stylist_schedule = get_all_schedules(
            session,
            filters=[
                WorkSchedule.stylist_id == stylist_id,
                WorkSchedule.day_of_week == weekday,
            ],
        )
        stylist_appointments = get_all_appointments(
            session,
            filters=[
                Appointment.stylist_id == stylist_id,
                Appointment.appointment_time.cast(Date) == appointment_date.date(),
            ],
        )

        service_duration = get_service(session, service_id).duration_minutes
        unavailable_intervals = calculate_unavailable_intervals(stylist_appointments)
        available_intervals = calculate_available_intervals(
            unavailable_intervals,
            stylist_schedule,
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
def tool_list_stylists() -> str:
    """
    Call to list all stylists and information about them. Useful to get the ID of the
    stylist to book an appointment or check its available hours.
    """
    with Session() as db_session:
        stylists = get_all_stylists(db_session)
        str_stylists = "These are the stylists:\n"
        for stylist in stylists:
            str_stylists += f"- {str(stylist)}\n"
    return str_stylists


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
    stylists = get_all_stylists(session)
    str_available_hours = f"Available hours for {appointment_date}:\n"
    for stylist in stylists:
        str_available_hours += f"{stylist.name}:\n"
        stylist_available_hours = _stylist_available_hours(
            appointment_date,
            service_id,
            stylist.id,
        )
        for available_hour in stylist_available_hours:
            str_available_hours += f"\t- {available_hour}\n"
    return str_available_hours


@tool
def tool_stylist_available_hours(
    appointment_date: str,
    service_id: int,
    stylist_id: int,
):
    """
    Call to list all available hours for a service and a stylist in a date.

    Params:
        appointment_date (date): Appointment date in the format "%Y-%m-%d"
        service_id (int): Identifier of the service for the appointment
        stylist_id (int): Identifier Team member the client would like
    """
    str_free_hours = f"Available hours for {appointment_date}:\n"
    for free_hour in _stylist_available_hours(appointment_date, service_id, stylist_id):
        str_free_hours += f"- {free_hour}\n"
    return str_free_hours


@tool
def tool_save_appointment(
    customer_id: int,
    stylist_id: int,
    service_id: int,
    appointment_datetime: str,
):
    """
    Call to save an appointment in the database.

    Params:
        customer_id (int): Identifier of the customer
        stylist_id (int): Identifier of the stylist
        service_id (int): Identifier of the service
        appointment_datetime (str): Appointment date and time in the format "%Y-%m-%d %H:%M:%S"
    """
    with Session() as session:
        appointment = AppointmentCreate(
            appointment_time=appointment_datetime,
            customer_id=customer_id,
            stylist_id=stylist_id,
            service_id=service_id,
        )
        create_appointment(session, appointment)
    return "Appointment saved successfully."


@tool
def tool_list_customer_appointments(customer_id: int):
    """
    Call to list all appointments for a customer.

    Params:
        customer_id (int): Identifier of the customer
    """
    with Session() as session:
        appointments = get_all_appointments(
            session,
            filters=[Appointment.customer_id == customer_id],
        )
        str_appointments = "These are the appointments:\n"
        for appointment in appointments:
            str_appointments += f"- {str(appointment)}\n"
    return str_appointments


@tool
def tool_update_appointment(
    appointment_id: int,
    appointment_datetime: str,
):
    """
    Call to update an appointment in the database.

    Params:
        appointment_id (int): Identifier of the appointment
        appointment_datetime (str): Appointment date and time in the format "%Y-%m-%d %H:%M:%S"
    """
    with Session() as session:
        appointment = AppointmentCreate(
            appointment_time=appointment_datetime,
        )
        update_appointment(session, appointment_id, appointment)
    return "Appointment updated successfully."


@tool
def tool_delete_appointment(appointment_id: int):
    """
    Call to delete an appointment from the database.

    Params:
        appointment_id (int): Identifier of the appointment
    """
    with Session() as session:
        delete_appointment(session, appointment_id)
    return "Appointment deleted successfully."


if __name__ == "__main__":
    available_slots = _stylist_available_hours("2025-10-11", 3, 3)
    print(available_slots)
