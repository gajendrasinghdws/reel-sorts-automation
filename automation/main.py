import argparse
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config import DOWNLOAD_DIR
from db import (
    get_accounts, reel_exists, create_reel, update_reel,
    get_next_upload, get_old_uploaded, normalize_source_key
)
from instagram import discover_latest, download as download_reel
from hash_utils import sha256_file
from drive import upload_video as drive_upload, download_file, delete_file
from youtube import upload_video as youtube_upload
from title_generator import make_title

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def download_one():
    # Manual URLs submitted from the dashboard get priority.
    from db import get_next_queued_manual
    manual = get_next_queued_manual()

    if manual:
        try:
            update_reel(manual["id"], {"status": "downloading"})
            path, info = download_reel(manual["instagram_url"], DOWNLOAD_DIR)
            digest = sha256_file(path)

            from db import sb
            existing = (
                sb.table("reels")
                .select("id")
                .eq("local_sha256", digest)
                .neq("id", manual["id"])
                .limit(1)
                .execute()
                .data
            )
            if existing:
                update_reel(manual["id"], {
                    "status": "skipped",
                    "local_sha256": digest,
                    "error_message": "Duplicate content hash",
                })
                path.unlink(missing_ok=True)
                print("Manual URL resolved to duplicate content; skipped.")
                return

            drive_id = drive_upload(str(path), path.name)
            update_reel(manual["id"], {
                "status": "downloaded",
                "local_sha256": digest,
                "drive_file_id": drive_id,
                "drive_file_name": path.name,
                "downloaded_at": now_iso(),
                "caption": info.get("description") or info.get("title") or manual.get("caption"),
                "title_hint": info.get("title") or manual.get("title_hint"),
            })
            path.unlink(missing_ok=True)
            print(f"Manual Reel downloaded to Drive: {path.name}")
            return
        except Exception as exc:
            update_reel(manual["id"], {
                "status": "failed",
                "error_message": str(exc)[:2000],
            })
            raise

    accounts = get_accounts()
    if not accounts:
        print("No active Instagram accounts and no queued manual URL.")
        return

    for account in accounts:
        username = account["username"]
        try:
            item = discover_latest(username)
            source_key = normalize_source_key(item["url"])

            if reel_exists(source_key):
                print(f"Already known, skipping: {source_key}")
                continue

            reel = create_reel({
                "user_id": account["user_id"],
                "instagram_account_id": account["id"],
                "instagram_url": item["url"],
                "source_media_id": item["media_id"],
                "source_key": source_key,
                "caption": item["caption"],
                "title_hint": item["title_hint"],
                "status": "downloading",
            })

            try:
                path, info = download_reel(item["url"], DOWNLOAD_DIR)
                digest = sha256_file(path)

                from db import sb
                existing = (
                    sb.table("reels")
                    .select("id")
                    .eq("local_sha256", digest)
                    .neq("id", reel["id"])
                    .limit(1)
                    .execute()
                    .data
                )
                if existing:
                    update_reel(reel["id"], {
                        "status": "skipped",
                        "local_sha256": digest,
                        "error_message": "Duplicate content hash",
                    })
                    print(f"Duplicate content, skipped: {path.name}")
                    path.unlink(missing_ok=True)
                    continue

                drive_id = drive_upload(str(path), path.name)
                update_reel(reel["id"], {
                    "status": "downloaded",
                    "local_sha256": digest,
                    "drive_file_id": drive_id,
                    "drive_file_name": path.name,
                    "downloaded_at": now_iso(),
                })
                print(f"Downloaded to Drive: {path.name}")
                path.unlink(missing_ok=True)
                return
            except Exception as exc:
                update_reel(reel["id"], {
                    "status": "failed",
                    "error_message": str(exc)[:2000],
                })
                print(f"Failed {username}: {exc}")
        except Exception as exc:
            print(f"Discovery failed for {username}: {exc}")

    print("No new Reel was downloaded.")

def upload_one():
    reel = get_next_upload()
    if not reel:
        print("No pending downloaded Reel.")
        return

    update_reel(reel["id"], {"status": "uploading"})
    temp = Path(DOWNLOAD_DIR)
    temp.mkdir(parents=True, exist_ok=True)
    filename = reel.get("drive_file_name") or f'{reel["id"]}.mp4'
    path = temp / filename

    try:
        download_file(reel["drive_file_id"], str(path))
        title = make_title(
            reel.get("caption", ""),
            reel.get("title_hint", ""),
            filename,
        )
        video_id = youtube_upload(
            str(path),
            title,
            reel.get("caption", ""),
        )
        update_reel(reel["id"], {
            "status": "uploaded",
            "youtube_video_id": video_id,
            "uploaded_at": now_iso(),
        })
        print(f"Uploaded to YouTube: {video_id}")
    except Exception as exc:
        update_reel(reel["id"], {
            "status": "downloaded",
            "error_message": str(exc)[:2000],
        })
        raise
    finally:
        path.unlink(missing_ok=True)

def cleanup():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for reel in get_old_uploaded():
        uploaded_at = reel.get("uploaded_at")
        if not uploaded_at:
            continue
        dt = datetime.fromisoformat(uploaded_at.replace("Z", "+00:00"))
        if dt > cutoff:
            continue
        try:
            delete_file(reel["drive_file_id"])
            update_reel(reel["id"], {
                "drive_deleted_at": now_iso(),
                "drive_file_id": None,
            })
            print(f"Deleted Drive file for reel {reel['id']}")
        except Exception as exc:
            print(f"Cleanup failed for {reel['id']}: {exc}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "upload", "cleanup"])
    args = parser.parse_args()

    if args.command == "download":
        download_one()
    elif args.command == "upload":
        upload_one()
    else:
        cleanup()

if __name__ == "__main__":
    main()
