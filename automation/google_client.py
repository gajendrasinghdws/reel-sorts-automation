import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload",
]

def get_credentials() -> Credentials:
    raw = os.getenv("GOOGLE_TOKEN_JSON")
    if not raw:
        path = Path("oauth/token.json")
        if not path.exists():
            raise RuntimeError("Missing GOOGLE_TOKEN_JSON and oauth/token.json")
        raw = path.read_text(encoding="utf-8")
    info = json.loads(raw)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("Google credentials are invalid or cannot be refreshed.")
    return creds

def drive_service():
    return build("drive", "v3", credentials=get_credentials(), cache_discovery=False)

def youtube_service():
    return build("youtube", "v3", credentials=get_credentials(), cache_discovery=False)
