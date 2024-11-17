from datetime import time

from db import engine, Session
from db.models import Base
from db.models import Stylist, WorkSchedule

def create_tables():
    # Connect to the new database and create tables
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

def poblate_test_database():
    session = Session()
    instances = []

    # Adding stylists
    stylist1 = Stylist(name="Jane Doe", specialty="Haircut")
    instances.append(stylist1)
    for day in range(5): # From monday (0) to friday (4)
        instances.append(WorkSchedule(stylist=stylist1, day_of_week=day, start_time=time(9, 0), end_time=time(14, 0)))
        instances.append(WorkSchedule(stylist=stylist1, day_of_week=day, start_time=time(17, 0), end_time=time(20, 0)))
    instances.append(WorkSchedule(stylist=stylist1, day_of_week=5, start_time=time(9, 30), end_time=time(14, 0)))

    # Commit to the database
    session.add_all(instances)
    session.commit()


if __name__ == "__main__":
    create_tables()
    poblate_test_database()

