import datetime
import logging
import os.path
from typing import List, Optional
from zoneinfo import ZoneInfo
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

CALENDAR_TZ = ZoneInfo("America/New_York")


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


def _parse_range_bound(value: Optional[str], *, end_of_day: bool) -> Optional[datetime.datetime]:
    """Parse RFC3339 or YYYY-MM-DD into an aware datetime in CALENDAR_TZ."""
    if not value or not str(value).strip():
        return None
    s = str(value).strip()
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            d = datetime.date.fromisoformat(s)
            t = datetime.time(23, 59, 59) if end_of_day else datetime.time(0, 0, 0)
            return datetime.datetime.combine(d, t, tzinfo=CALENDAR_TZ)
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=CALENDAR_TZ)
        else:
            dt = dt.astimezone(CALENDAR_TZ)
        return dt
    except ValueError:
        raise ValueError(
            f"Invalid date/time: {value!r}. Use YYYY-MM-DD or RFC3339 (e.g. 2026-04-05T09:00:00-04:00)."
        ) from None


def _event_line(item: dict) -> str:
    summary = item.get("summary") or "(No title)"
    start = item.get("start") or {}
    end = item.get("end") or {}
    start_s = start.get("dateTime") or start.get("date", "")
    end_s = end.get("dateTime") or end.get("date", "")
    loc = item.get("location") or ""
    parts = [f"- {summary}", f"  start: {start_s}", f"  end: {end_s}"]
    if loc:
        parts.append(f"  location: {loc}")
    return "\n".join(parts)


def list_calendar_events(
    time_min_iso: Optional[str] = None,
    time_max_iso: Optional[str] = None,
    max_results_per_page: int = 250,
) -> str:
    """
    List events on the primary calendar between time_min and time_max (inclusive window).
    Paginates until all events in the range are retrieved.
    If bounds are omitted, uses start of today through 30 days ahead (America/New_York).
    """
    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.now(CALENDAR_TZ)
    time_min = _parse_range_bound(time_min_iso, end_of_day=False)
    time_max = _parse_range_bound(time_max_iso, end_of_day=True)
    if time_min is None:
        time_min = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if time_max is None:
        time_max = time_min + datetime.timedelta(days=30)

    time_min_s = time_min.isoformat()
    time_max_s = time_max.isoformat()

    items: List[dict] = []
    page_token: Optional[str] = None
    while True:
        req = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min_s,
                timeMax=time_max_s,
                maxResults=max_results_per_page,
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token,
            )
            .execute()
        )
        items.extend(req.get("items") or [])
        page_token = req.get("nextPageToken")
        if not page_token:
            break

    if not items:
        return (
            f"No events between {time_min_s} and {time_max_s} "
            f"(America/New_York calendar window)."
        )

    header = (
        f"Calendar events ({len(items)} found) from {time_min_s} to {time_max_s} "
        f"(America/New_York):\n\n"
    )
    return header + "\n\n".join(_event_line(ev) for ev in items)

