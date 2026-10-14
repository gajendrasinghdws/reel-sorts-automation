import re

MAX_TITLE = 100

STOP = {
    "the","and","for","with","this","that","from","your","you","are","was",
    "have","has","into","about","instagram","reel","reels"
}

def make_title(caption: str = "", title_hint: str = "", filename: str = "") -> str:
    raw = (title_hint or caption or filename or "Daily Reel").strip()
    raw = re.sub(r"https?://\S+", "", raw)
    raw = re.sub(r"\s+", " ", raw)
    raw = raw.replace("\n", " ").strip(" -|•")
    if not raw:
        raw = "Daily Reel"
    if len(raw) <= MAX_TITLE:
        return raw

    words = raw.split()
    picked = []
    length = 0
    for word in words:
        next_len = length + len(word) + (1 if picked else 0)
        if next_len > MAX_TITLE:
            break
        picked.append(word)
        length = next_len
    return " ".join(picked).rstrip(".,:;!?-")
