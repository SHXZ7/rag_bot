import os
import tempfile
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]   # project root (interhsla/)


def _get_raw_cookie_path(env_var: str, filename: str) -> Path | None:
    """Check for raw cookie content in environment variables and write to a temp file."""
    raw_content = os.environ.get(env_var)
    if not raw_content:
        return None
    
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / filename
    try:
        # Write/overwrite the raw cookies text
        temp_file.write_text(raw_content.strip(), encoding="utf-8")
        print(f"[cookies] Dynamically wrote cookies from env var '{env_var}' to: {temp_file}")
        return temp_file
    except Exception as e:
        print(f"[cookies] Error writing raw cookies for '{env_var}': {e}")
        return None


def get_youtube_cookiefile() -> str | None:
    """Return path to YouTube cookies file, or None if not found.

    Search order:
      1. YT_COOKIES_RAW env var (written to temp file)
      2. YTDLP_COOKIES_YT env var (file path)
      3. ytcookies.txt  (project root)
      4. YTDLP_COOKIES / YTDLP_COOKIES_FILE env var  (generic fallback file path)
      5. cookies.txt    (project root, last resort)
    """
    candidates = []

    # 1. Check raw content env var (recommended for PaaS deployments)
    temp_raw = _get_raw_cookie_path("YT_COOKIES_RAW", "ytcookies_temp.txt")
    if temp_raw:
        candidates.append(temp_raw)

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
      1. IG_COOKIES_RAW env var (written to temp file)
      2. YTDLP_COOKIES / YTDLP_COOKIES_FILE env var (file path)
      3. cookies_www.instagram.com.txt  (project root)
      4. www.instagram.com_cookies.txt  (project root)
      5. cookies.txt                    (project root)
    """
    candidates = []

    # 1. Check raw content env var (recommended for PaaS deployments)
    temp_raw = _get_raw_cookie_path("IG_COOKIES_RAW", "cookies_temp.txt")
    if temp_raw:
        candidates.append(temp_raw)

    configured = (
        os.environ.get("YTDLP_COOKIES")
        or os.environ.get("YTDLP_COOKIES_FILE")
    )
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

