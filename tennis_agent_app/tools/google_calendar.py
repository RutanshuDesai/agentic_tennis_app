import datetime
import json
import logging
import os.path
from typing import List, Optional
from zoneinfo import ZoneInfo
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv

dotenv_path = os.environ.get("DOTENV_PATH")
if dotenv_path:
    load_dotenv(os.path.expandvars(dotenv_path))
else:
    load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger(__name__)

RUNTIME_ENV = os.environ.get("RUNTIME_ENV", "local")

CREDS_FILE = os.environ.get("GOOGLE_CALENDAR_CRED_FILE_PATH")
TOKEN_FILE = os.environ.get("GOOGLE_CALENDAR_TOKEN_FILE_PATH")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
CREDS_SECRET_NAME = os.environ.get("GOOGLE_CALENDAR_CREDS_SECRET", "google-calendar-creds")
TOKEN_SECRET_NAME = os.environ.get("GOOGLE_CALENDAR_TOKEN_SECRET", "google-calendar-token")

CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
CALENDAR_IDS_TO_CHECK = [
    cid.strip()
    for cid in os.environ.get("GOOGLE_CALENDAR_IDS_TO_CHECK", "primary").split(",")
    if cid.strip()
]

SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDAR_TZ = ZoneInfo("America/New_York")


def _get_secret(secret_name: str) -> str:
    """Fetch the latest version of a secret from GCP Secret Manager."""
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def _update_secret(secret_name: str, payload: str) -> None:
    """Add a new version of the secret (persists the refreshed token)."""
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}"
    client.add_secret_version(
        request={"parent": parent, "payload": {"data": payload.encode("UTF-8")}}
    )
    logger.info("Updated secret %s with new token version.", secret_name)


def _run_oauth_flow():
    """Run interactive OAuth flow (local development only)."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds


def _get_credentials():
    if RUNTIME_ENV == "cloud":
        return _get_credentials_from_secret_manager()
    return _get_credentials_local()


def _get_credentials_from_secret_manager():
    """Load OAuth token from Secret Manager; refresh and persist if expired."""
    token_json = _get_secret(TOKEN_SECRET_NAME)
    creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                _update_secret(TOKEN_SECRET_NAME, creds.to_json())
            except RefreshError:
                raise RuntimeError(
                    "OAuth refresh token expired or revoked. "
                    "Re-run the local OAuth flow to generate a new token, "
                    "then upload it to Secret Manager."
                )
        else:
            raise RuntimeError(
                "No valid credentials in Secret Manager. "
                "Run the OAuth flow locally and upload the token."
            )

    return creds


def _get_credentials_local():
    """Original local-file credential flow for development."""
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

    event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
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


def _event_line(item: dict, calendar_id: str = "") -> str:
    summary = item.get("summary") or "(No title)"
    start = item.get("start") or {}
    end = item.get("end") or {}
    start_s = start.get("dateTime") or start.get("date", "")
    end_s = end.get("dateTime") or end.get("date", "")
    loc = item.get("location") or ""
    parts = [f"- {summary}", f"  start: {start_s}", f"  end: {end_s}"]
    if calendar_id:
        parts.append(f"  calendar: {calendar_id}")
    if loc:
        parts.append(f"  location: {loc}")
    return "\n".join(parts)


def list_calendar_events(
    time_min_iso: Optional[str] = None,
    time_max_iso: Optional[str] = None,
    max_results_per_page: int = 250,
) -> str:
    """
    List events across all calendars in CALENDAR_IDS_TO_CHECK between time_min
    and time_max (inclusive window). Results are merged and sorted by start time.
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

    all_items: List[tuple] = []
    for cal_id in CALENDAR_IDS_TO_CHECK:
        page_token: Optional[str] = None
        while True:
            req = (
                service.events()
                .list(
                    calendarId=cal_id,
                    timeMin=time_min_s,
                    timeMax=time_max_s,
                    maxResults=max_results_per_page,
                    singleEvents=True,
                    orderBy="startTime",
                    pageToken=page_token,
                )
                .execute()
            )
            for item in req.get("items") or []:
                all_items.append((item, cal_id))
            page_token = req.get("nextPageToken")
            if not page_token:
                break

    all_items.sort(
        key=lambda pair: pair[0].get("start", {}).get("dateTime")
        or pair[0].get("start", {}).get("date", "")
    )

    if not all_items:
        return (
            f"No events between {time_min_s} and {time_max_s} "
            f"(America/New_York calendar window)."
        )

    header = (
        f"Calendar events ({len(all_items)} found) from {time_min_s} to {time_max_s} "
        f"(America/New_York, calendars checked: {', '.join(CALENDAR_IDS_TO_CHECK)}):\n\n"
    )
    return header + "\n\n".join(_event_line(ev, cal_id) for ev, cal_id in all_items)

