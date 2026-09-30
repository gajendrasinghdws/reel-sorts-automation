from pathlib import Path
import re
import yt_dlp

def normalize_username(username: str) -> str:
    value = username.strip()
    if value.startswith("@"):
        value = value[1:]
    return value.strip().strip("/")

def reel_url(url_or_username: str) -> str:
    value = url_or_username.strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"https://www.instagram.com/{normalize_username(value)}/"

def discover_latest(url_or_username: str):
    """
    Returns a dict for the latest extractable Instagram item.

    Instagram extraction is inherently subject to platform changes.
    We keep this isolated so it can be replaced by an authorized API adapter.
    """
    target = reel_url(url_or_username)
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "playlistend": 1,
        "noplaylist": False,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(target, download=False)

    entries = info.get("entries") if isinstance(info, dict) else None
    if entries:
        entry = next((x for x in entries if x), None)
        if entry:
            info = entry

    webpage_url = info.get("webpage_url") or info.get("original_url") or target
    media_id = str(info.get("id") or webpage_url)
    caption = info.get("description") or info.get("title") or ""
    return {
        "url": webpage_url,
        "media_id": media_id,
        "caption": caption,
        "title_hint": info.get("title") or "",
    }

def download(url: str, out_dir: str) -> tuple[Path, dict]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    opts = {
        "outtmpl": str(Path(out_dir) / "%(id)s.%(ext)s"),
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
        mp4 = path.with_suffix(".mp4")
        if mp4.exists():
            path = mp4
        return path, info
