from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_accounts():
    return sb.table("instagram_accounts").select("*").eq("active", True).execute().data

def reel_exists(source_key: str) -> bool:
    result = (
        sb.table("reels")
        .select("id")
        .eq("source_key", source_key)
        .limit(1)
        .execute()
    )
    return bool(result.data)

def create_reel(payload: dict):
    return sb.table("reels").insert(payload).execute().data[0]

def update_reel(reel_id: str, payload: dict):
    return sb.table("reels").update(payload).eq("id", reel_id).execute().data[0]

def get_next_queued_manual():
    result = (
        sb.table("reels")
        .select("*")
        .eq("status", "queued")
        .is_("instagram_account_id", "null")
        .order("created_at", desc=False)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def get_next_upload():
    result = (
        sb.table("reels")
        .select("*")
        .eq("status", "downloaded")
        .is_("youtube_video_id", "null")
        .not_.is_("drive_file_id", "null")
        .order("downloaded_at", desc=False)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def get_old_uploaded():
    result = (
        sb.table("reels")
        .select("*")
        .eq("status", "uploaded")
        .not_.is_("drive_file_id", "null")
        .not_.is_("uploaded_at", "null")
        .execute()
    )
    return result.data

def insert_manual_reel(user_id: str, url: str):
    source_key = normalize_source_key(url)
    if reel_exists(source_key):
        return None, "duplicate"
    row = create_reel({
        "user_id": user_id,
        "instagram_url": url,
        "source_key": source_key,
        "status": "queued",
    })
    return row, "created"

def normalize_source_key(url: str) -> str:
    value = url.strip().split("?")[0].rstrip("/")
    return value.lower()
