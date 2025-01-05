from datetime import datetime

import streamlit as st
from db import Session
from db.crud import create_appointment
from db.crud import create_customer
from db.crud import create_service
from db.crud import create_stylist
from db.crud import create_work_schedule
from db.crud import get_all_customers
from db.crud import get_all_services
from db.crud import get_all_stylists
from db.schemas import AppointmentCreate
from db.schemas import CustomerCreate
from db.schemas import ServiceCreate
from db.schemas import StylistCreate
from db.schemas import WorkScheduleCreate


def main():
    st.title("Beauty Salon Management")

    # Sidebar navigation
    menu = ["Customers", "Stylists", "Services", "Work Schedules", "Appointments"]
    choice = st.sidebar.selectbox("Menu", menu)

    db_session = Session()

    if choice == "Customers":
        st.header("Customers")
        # List all customers
        customers = get_all_customers(db_session)
        st.write("### All Customers")
        if customers:
            st.table([customer.model_dump() for customer in customers])
        else:
            st.write("No customers found.")

        # Add a new customer
        st.write("### Add Customer")
        with st.form("add_customer"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                new_customer = CustomerCreate(name=name, email=email, phone=phone)
                create_customer(db_session, new_customer)
                st.success("Customer added successfully")

    elif choice == "Stylists":
        st.header("Stylists")
        # List all stylists
        stylists = get_all_stylists(db_session)
        st.write("### All Stylists")
        if stylists:
            st.table([stylist.model_dump() for stylist in stylists])
        else:
            st.write("No stylists found.")
        # Add a new stylist
        st.write("### Add Stylist")
        with st.form("add_stylist"):
            name = st.text_input("Name")
            specialty = st.text_input("Specialty")
            submitted = st.form_submit_button("Add Stylist")
            if submitted:
                new_stylist = StylistCreate(name=name, specialty=specialty)
                create_stylist(db_session, new_stylist)
                st.success("Stylist added successfully")

    elif choice == "Services":
        st.header("Services")
        # List all services
        services = get_all_services(db_session)
        st.write("### All Services")
        if services:
            st.table([service.model_dump() for service in services])
        else:
            st.write("No services found.")

        # Add a new service
        st.write("### Add Service")
        with st.form("add_service"):
            name = st.text_input("Service Name")
            price = st.number_input("Price", min_value=0.0)
            duration = st.number_input("Duration (minutes)", min_value=0)
            submitted = st.form_submit_button("Add Service")
            if submitted:
                new_service = ServiceCreate(
                    name=name,
                    price=price,
                    duration_minutes=duration,
                )
                create_service(db_session, new_service)
                st.success("Service added successfully")

    elif choice == "Work Schedules":
        st.header("Work Schedules")
        # Add a new work schedule
        st.write("### Add Work Schedule")
        with st.form("add_schedule"):
            stylist_id = st.number_input("Stylist ID", min_value=1)
            day_of_week = st.selectbox(
                "Day of Week",
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
            )
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            submitted = st.form_submit_button("Add Schedule")
            if submitted:
                day_of_week_num = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ].index(day_of_week)
                new_schedule = WorkScheduleCreate(
                    stylist_id=stylist_id,
                    day_of_week=day_of_week_num,
                    start_time=start_time,
                    end_time=end_time,
                )
                create_work_schedule(db_session, new_schedule)
                st.success("Schedule added successfully")

    elif choice == "Appointments":
        st.header("Appointments")
        # Add a new appointment
        st.write("### Add Appointment")
        with st.form("add_appointment"):
            customer_id = st.number_input("Customer ID", min_value=1)
            stylist_id = st.number_input("Stylist ID", min_value=1)
            service_id = st.number_input("Service ID", min_value=1)
            appointment_date = st.date_input("Appointment Date", value="today")
            appointment_time = st.time_input("Appointmen Time", value="now")
            submitted = st.form_submit_button("Add Appointment")
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            if submitted:
                new_appointment = AppointmentCreate(
                    customer_id=customer_id,
                    stylist_id=stylist_id,
                    service_id=service_id,
                    appointment_time=appointment_datetime,
                )
                create_appointment(db_session, new_appointment)
                st.success("Appointment added successfully")

    db_session.close()


if __name__ == "__main__":
    main()
