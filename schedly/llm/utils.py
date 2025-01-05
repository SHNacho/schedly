from datetime import date
from datetime import datetime
from datetime import timedelta

from db import Session
from db.crud import get_appointment
from db.crud import get_service


def print_stream(stream):
    """
    Funciton to print the stream nicely
    """
    messages = stream["messages"]
    for message in messages:
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def calculate_unavailable_intervals(appointments: list):
    unavailable_intervals = [
        (
            appointment.appointment_time.time(),
            (
                datetime.combine(date.today(), appointment.appointment_time.time())
                + timedelta(minutes=appointment.service.duration_minutes)
            ).time(),
        )
        for appointment in appointments
    ]

    # Merge overlapping intervals
    i = 1
    while i < len(unavailable_intervals):
        if unavailable_intervals[i][0] == unavailable_intervals[i - 1][1]:
            unavailable_intervals[i - 1] = (
                unavailable_intervals[i - 1][0],
                unavailable_intervals[i][1],
            )
            unavailable_intervals.pop(i)

    return unavailable_intervals


def calculate_available_intervals(unavailable_intervals, work_schedule):
    available_intervals = [
        (s.start_time, s.end_time) for s in work_schedule
    ]  # start with all the available intervals

    updated_intervals = []

    for a_start, a_end in available_intervals:
        current_intervals = [(a_start, a_end)]

        for u_start, u_end in unavailable_intervals:
            new_intervals = []
            for c_start, c_end in current_intervals:
                if u_start >= c_end or u_end <= c_start:
                    new_intervals.append((c_start, c_end))
                else:
                    if u_start > c_start:
                        new_intervals.append((c_start, u_start))
                    if u_end < c_end:
                        new_intervals.append((u_end, c_end))

            current_intervals = new_intervals

        updated_intervals.extend(current_intervals)

    return updated_intervals


def time_interval_into_slots(start_time, end_time, interval):
    """
    Function to convert a time interval into slots.
    """
    slots = []
    current_time = start_time
    while current_time < end_time:
        slot_end_time = (
            datetime.combine(date.today(), current_time) + timedelta(minutes=interval)
        ).time()
        if slot_end_time < end_time:
            slots.append(current_time)
        current_time = slot_end_time
    return slots
