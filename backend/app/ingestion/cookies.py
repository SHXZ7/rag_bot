import os
from pathlib import Path


def get_cookiefile():
    configured = (
        os.environ.get("YTDLP_COOKIES")
        or os.environ.get("YTDLP_COOKIES_FILE")
    )

    candidates = []
    if configured:
        candidates.append(Path(configured))

    project_root = Path(__file__).resolve().parents[3]
    candidates.extend([
        project_root / "cookies_www.instagram.com.txt",
        project_root / "www.instagram.com_cookies.txt",
        project_root / "cookies.txt"
    ])

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return None
