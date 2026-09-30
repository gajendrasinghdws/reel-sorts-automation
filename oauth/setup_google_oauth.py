from pathlib import Path
import json

from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS = ROOT / "oauth" / "credentials.json"
TOKEN = ROOT / "oauth" / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload",
]

def main():
    if not CREDENTIALS.exists():
        raise SystemExit(
            "Missing oauth/credentials.json. Create a Google Desktop OAuth client "
            "and download the JSON with this filename."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved {TOKEN}")
    print("Copy the entire token.json content into the GitHub secret GOOGLE_TOKEN_JSON.")

if __name__ == "__main__":
    main()
