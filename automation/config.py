import os

def require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value

SUPABASE_URL = require("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = require("SUPABASE_SERVICE_ROLE_KEY")
DRIVE_FOLDER_ID = require("DRIVE_FOLDER_ID")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_DOWNLOAD_SECONDS = int(os.getenv("MAX_DOWNLOAD_SECONDS", "1800"))
