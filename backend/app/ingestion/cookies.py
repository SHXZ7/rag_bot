import os
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]   # project root (interhsla/)


def get_youtube_cookiefile() -> str | None:
    """Return path to YouTube cookies file, or None if not found.

    Search order:
      1. YTDLP_COOKIES_YT env var
      2. ytcookies.txt  (project root)
      3. YTDLP_COOKIES / YTDLP_COOKIES_FILE env var  (generic fallback)
      4. cookies.txt    (project root, last resort)
    """
    candidates = []

    yt_env = os.environ.get("YTDLP_COOKIES_YT")
    if yt_env:
        candidates.append(Path(yt_env))

    candidates.append(_ROOT / "ytcookies.txt")

    generic_env = (
        os.environ.get("YTDLP_COOKIES")
        or os.environ.get("YTDLP_COOKIES_FILE")
    )
    if generic_env:
        candidates.append(Path(generic_env))

    candidates.append(_ROOT / "cookies.txt")

    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def get_cookiefile() -> str | None:
    """Return path to the Instagram / generic cookies file, or None.

    Search order:
      1. YTDLP_COOKIES / YTDLP_COOKIES_FILE env var
      2. cookies_www.instagram.com.txt  (project root)
      3. www.instagram.com_cookies.txt  (project root)
      4. cookies.txt                    (project root)
    """
    configured = (
        os.environ.get("YTDLP_COOKIES")
        or os.environ.get("YTDLP_COOKIES_FILE")
    )

    candidates = []
    if configured:
        candidates.append(Path(configured))

    candidates.extend([
        _ROOT / "cookies_www.instagram.com.txt",
        _ROOT / "www.instagram.com_cookies.txt",
        _ROOT / "cookies.txt",
    ])

    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def get_cookiefile_for_url(url: str) -> str | None:
    """Pick the right cookies file based on the URL's platform."""
    if "youtube.com" in url or "youtu.be" in url:
        return get_youtube_cookiefile()
    return get_cookiefile()
