import random
from datetime import datetime
from datetime import time

from db import engine
from db import Session
from db.models import Appointment
from db.models import Base
from db.models import Customer
from db.models import Service
from db.models import Stylist
from db.models import StylistServices
from db.models import WorkSchedule
from faker import Faker


def random_time_between(start_time, end_time):
    start_seconds = start_time.hour * 3600 + start_time.minute * 60
    end_seconds = end_time.hour * 3600 + end_time.minute * 60
    random_seconds = random.randint(start_seconds, end_seconds)
    return time(random_seconds // 3600, (random_seconds % 3600) // 60)


def drop_tables():
    Base.metadata.drop_all(engine)
    print("All tables dropbed successfully")


def create_tables():
    # Connect to the new database and create tables
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")


# Helper function to generate random times
def random_time():
    return time(hour=random.randint(9, 17), minute=random.choice([0, 30]))

schedules = {
    "morning": {
        "start": [
            time(9, 0),
            time(9, 30),
            time(10, 0),
            time(10, 30),
            time(11, 0),
            time(12, 0),
        ],
        "end": [
            time(14, 0),
            time(14, 30),
            time(15, 0),
            time(15, 30),
            time(16, 0),
            time(16, 30),
            time(17, 0),
        ],
    },
    "afternoon": {
        "start": [time(17, 0), time(17, 30), time(18, 0)],
        "end": [time(20, 0), time(20, 30), time(21, 0), time(21, 30)],
    },
}


def populate_fake_db(session):
    # Initialize Faker
    faker = Faker()

    # Create fake customers
    customers = [
        Customer(
            name=faker.name(),
            email=faker.unique.email(),
            phone=faker.unique.phone_number(),
            created_at=faker.date_time_this_year(),
        )
        for _ in range(10)
    ]
    session.add_all(customers)
    session.flush()  # Flush to get customer IDs
    print("Customer table populated")

    # Create fake stylists
    stylists = [
        Stylist(
            name=faker.name(),
            created_at=faker.date_time_this_year(),
        )
        for _ in range(5)
    ]
    session.add_all(stylists)
    session.flush()  # Flush to get stylist IDs
    print("Stylists table populated")

    # Create fake services
    services = [
        Service(
            name="nails",
            price=15,
            duration_minutes=30,
            created_at=faker.date_time_this_year(),
        ),
        Service(
            name="hair cut",
            price=13.50,
            duration_minutes=30,
            created_at=faker.date_time_this_year(),
        ),
        Service(
            name="hair dye",
            price=35,
            duration_minutes=60,
            created_at=faker.date_time_this_year(),
        )
    ]
    session.add_all(services)
    session.flush()  # Flush to get service IDs
    print("Services table populated")

    # Associate stylists with services
    for stylist in stylists:
        services_for_stylist = random.sample(services, random.randint(1, len(services)))
        for service in services_for_stylist:
            session.add(StylistServices(stylist_id=stylist.id, service_id=service.id))
    print("StylystServices table populated")

    # Create work schedules for stylists
    for stylist in stylists:
        for day_of_week in range(7):  # Create schedules for the whole week
            if random.choice(
                [True, False],
            ):  # Randomly decide if stylist works on this day
                if random.choice(list(schedules.keys())) == "morning":
                    session.add(
                        WorkSchedule(
                            stylist_id=stylist.id,
                            day_of_week=day_of_week,
                            start_time=random.choice(schedules["morning"]["start"]),
                            end_time=random.choice(schedules["morning"]["end"]),
                            created_at=faker.date_time_this_year(),
                        ),
                    )
                else:
                    session.add(
                        WorkSchedule(
                            stylist_id=stylist.id,
                            day_of_week=day_of_week,
                            start_time=random.choice(schedules["afternoon"]["start"]),
                            end_time=random.choice(schedules["afternoon"]["end"]),
                            created_at=faker.date_time_this_year(),
                        ),
                    )

    session.flush()  # Flush to get all IDs
    print("WorkSchedule table populated")

    # Create fake appointments
    for _ in range(20):
        customer = random.choice(customers)
        stylist = random.choice(stylists)
        service = random.choice(services)
        appointment_date = faker.date_this_year()
        while True:
            available_weekdays = [
                schedule.day_of_week for schedule in stylist.work_schedules
            ]
            try:
                idx = available_weekdays.index(appointment_date.weekday())
            except ValueError:
                idx = None
            if idx is not None:
                break
            else:
                appointment_date = faker.date_this_year(after_today=True)
        appointment_time = random_time_between(
            stylist.work_schedules[idx].start_time,
            stylist.work_schedules[idx].end_time,
        )
        appointment_datetime = datetime.combine(appointment_date, appointment_time)

        session.add(
            Appointment(
                appointment_time=appointment_datetime,
                customer_id=customer.id,
                stylist_id=stylist.id,
                service_id=service.id,
                created_at=faker.date_time_this_year(),
            ),
        )
    print("Appointments table populated")

    # Commit all changes
    session.commit()
    print("Database populated with fake data.")


if __name__ == "__main__":
    #drop_tables()
    #create_tables()
    session = Session()
    populate_fake_db(session)
