import datetime
import logging
import os.path
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

CREDS_FILE = os.environ.get("GOOGLE_CALENDAR_CRED_FILE_PATH")
TOKEN_FILE = os.environ.get("GOOGLE_CALENDAR_TOKEN_FILE_PATH")

SCOPES = ['https://www.googleapis.com/auth/calendar']


def _run_oauth_flow():
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds


def _get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except RefreshError:
                logger.warning("Refresh token expired or revoked — re-authenticating via browser.")
                os.remove(TOKEN_FILE)
                creds = _run_oauth_flow()
        else:
            creds = _run_oauth_flow()

    return creds


def create_calendar_event(summary, start_time, end_time, description=""):
    creds = _get_credentials()

    service = build('calendar', 'v3', credentials=creds)

    event_body = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }

    event = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {event.get('htmlLink')}")

