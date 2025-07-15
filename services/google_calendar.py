from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db import Session
from db.crud import get_business
from db.crud import update_business
from db.schemas import BusinessCreate

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
    "https://www.googleapis.com/auth/calendar.acls",
    "https://www.googleapis.com/auth/calendar.calendars",
]


class GoogleCalendarClient:
    def __init__(self, business_id: str):
        self.session = Session()
        self.business_id = business_id
        self.business = get_business(self.session, business_id)
        self.creds = self.authenticate()

    def __del__(self):
        self.session.close()

    def authenticate(self):
        creds = None

        if self.business and self.business.google_credentials:
            creds = Credentials.from_authorized_user_info(
                self.business.google_credentials,
                SCOPES,
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)

            # Save updated credentials
            new_data = BusinessCreate(
                name=self.business.name,
                google_credentials=eval(creds.to_json()),
            )
            self.business = update_business(self.session, self.business_id, new_data)

        return creds

    def create_calendar(self, name):
        try:
            service = build("calendar", "v3", credentials=self.creds)
            new_calendar = service.calendars().insert(body={"summary": name}).execute()
            return new_calendar
        except HttpError as error:
            print(f"An error occurred: {error}")

    def share_calendar(self, calendar_id, email):
        try:
            service = build("calendar", "v3", credentials=self.creds)
            rule = {
                "scope": {
                    "type": "user",
                    "value": email,
                },
                "role": "writer",
            }
            return service.acl().insert(calendarId=calendar_id, body=rule).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")

    def add_event(
        self,
        calendar_id,
        summary,
        start_time,
        end_time,
        description=None,
        timezone="Europe/Madrid",
    ):
        """
        Add an event to a calendar.

        Args:
            calendar_id (str): ID of the calendar to add the event to.
            summary (str): Title of the event.
            start_time (str): ISO 8601 start time (e.g., "2025-06-09T10:00:00").
            end_time (str): ISO 8601 end time (e.g., "2025-06-09T11:00:00").
            description (str): Optional description.
            timezone (str): Timezone, default is "Europe/Madrid".
        """
        try:
            service = build("calendar", "v3", credentials=self.creds)
            event = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": start_time,
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": timezone,
                },
            }

            created_event = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )
            return created_event

        except HttpError as error:
            print(f"An error occurred: {error}")

    def delete_event(self, calendar_id, event_id):
        """
        Delete an event from a calendar.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event to delete.
        """
        try:
            service = build("calendar", "v3", credentials=self.creds)
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Event {event_id} deleted successfully.")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting the event: {error}")
            return False

    def update_event(
        self,
        calendar_id,
        event_id,
        summary=None,
        start_time=None,
        end_time=None,
        description=None,
        timezone="Europe/Madrid",
    ):
        """
        Update an event in a calendar.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event.
            summary (str): New title (optional).
            start_time (str): New start time (ISO 8601, optional).
            end_time (str): New end time (ISO 8601, optional).
            description (str): New description (optional).
            timezone (str): Timezone, default is "Europe/Madrid".
        """
        try:
            service = build("calendar", "v3", credentials=self.creds)

            # Fetch the current event
            event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )

            if summary:
                event["summary"] = summary
            if description:
                event["description"] = description
            if start_time:
                event["start"]["dateTime"] = start_time
                event["start"]["timeZone"] = timezone
            if end_time:
                event["end"]["dateTime"] = end_time
                event["end"]["timeZone"] = timezone

            updated_event = (
                service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )
            return updated_event

        except HttpError as error:
            print(f"An error occurred while updating the event: {error}")
            return None
