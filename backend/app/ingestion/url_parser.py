def detect_platform(url: str):

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"

    if "instagram.com" in url:
        return "instagram"

    raise ValueError("Unsupported URL")
