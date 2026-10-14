import os
from pathlib import Path
from dotenv import load_dotenv

# Local .env load karne ke liye
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

def require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    # Quotes ya hidden spaces remove karega
    return value.strip().strip("'").strip('"')

SUPABASE_URL = require("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = require("SUPABASE_SERVICE_ROLE_KEY")
DRIVE_FOLDER_ID = require("DRIVE_FOLDER_ID")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_DOWNLOAD_SECONDS = int(os.getenv("MAX_DOWNLOAD_SECONDS", "1800"))
