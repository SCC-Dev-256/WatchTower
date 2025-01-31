import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'  # Update with your path

def create_google_calendar_event(meeting_info):
    """Create a Google Calendar event from MeetingInfo."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': meeting_info.title,
        'location': meeting_info.location or 'Online',
        'description': meeting_info.description or '',
        'start': {
            'dateTime': meeting_info.date.isoformat(),
            'timeZone': 'America/Chicago', 
        },
        'end': {
            'dateTime': (meeting_info.date + timedelta(hours=1)).isoformat(),  # Assuming 1 hour duration
            'timeZone': 'America/Chicago',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}") 