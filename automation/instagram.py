import os
from pathlib import Path
import yt_dlp

def get_cookie_file() -> str | None:
    possible_paths = [
        Path("automation/cookies.txt"),
        Path("cookies.txt"),
        Path(__file__).resolve().parent / "cookies.txt",
    ]
    for p in possible_paths:
        if p.exists() and p.is_file() and p.stat().st_size > 0:
            return str(p)
    return None

def normalize_username(username: str) -> str:
    value = username.strip()
    if value.startswith("@"):
        value = value[1:]
    return value.strip().strip("/")

def reel_url(url_or_username: str) -> str:
    value = url_or_username.strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    # yt-dlp standard Instagram profile URL expect karta hai
    return f"https://www.instagram.com/{normalize_username(value)}/"

def discover_latest(url_or_username: str):
    target = reel_url(url_or_username)
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "playlistend": 5,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    cookie_path = get_cookie_file()
    if cookie_path:
        opts["cookiefile"] = cookie_path

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(target, download=False)

    entries = info.get("entries") if isinstance(info, dict) else None
    if entries:
        valid_entries = [x for x in entries if x]
        if valid_entries:
            info = valid_entries[0]

    webpage_url = info.get("webpage_url") or info.get("original_url") or info.get("url") or target
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
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        },
    }

    cookie_path = get_cookie_file()
    if cookie_path:
        opts["cookiefile"] = cookie_path

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
        mp4 = path.with_suffix(".mp4")
        if mp4.exists():
            path = mp4
        return path, info
