import re
from http.cookiejar import MozillaCookieJar

import requests

from app.ingestion.cookies import get_cookiefile


SHORTCODE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def extract_shortcode(url, info=None):
    info = info or {}

    value = info.get("display_id")
    if value and re.fullmatch(r"[\w-]{5,}", str(value)):
        return str(value)

    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#]+)", url)
    if match:
        return match.group(1)

    value = info.get("id")
    if (
        value
        and not str(value).isdigit()
        and re.fullmatch(r"[\w-]{5,}", str(value))
    ):
        return str(value)

    return None


def shortcode_to_media_id(shortcode):
    media_id = 0
    for char in shortcode:
        media_id = media_id * 64 + SHORTCODE_ALPHABET.index(char)

    return media_id


def _session(cookie_file=None):
    cookiefile = cookie_file or get_cookiefile()
    if not cookiefile:
        return None

    jar = MozillaCookieJar()
    jar.load(cookiefile, ignore_discard=True, ignore_expires=True)

    session = requests.Session()
    session.cookies.update(jar)
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "X-IG-App-ID": "936619743392459",
        "Referer": "https://www.instagram.com/"
    })

    return session


def fetch_profile_metadata(username, cookie_file=None):
    if not username:
        return {}

    session = _session(cookie_file)
    if session is None:
        return {}

    response = session.get(
        "https://www.instagram.com/api/v1/users/web_profile_info/",
        params={"username": username},
        timeout=20
    )
    response.raise_for_status()

    user = (
        response.json()
        .get("data", {})
        .get("user", {})
    )

    return {
        "creator": user.get("full_name") or user.get("username"),
        "follower_count": (
            user.get("edge_followed_by", {})
            .get("count")
        )
    }


def fetch_media_metadata(url, info=None, cookie_file=None):
    shortcode = extract_shortcode(url, info)
    if not shortcode:
        return {}

    session = _session(cookie_file)
    if session is None:
        return {}

    media_id = shortcode_to_media_id(shortcode)
    response = session.get(
        f"https://www.instagram.com/api/v1/media/{media_id}/info/",
        timeout=20
    )
    response.raise_for_status()

    items = response.json().get("items") or []
    item = items[0] if items else {}

    return {
        "views": (
            item.get("play_count")
            or item.get("ig_play_count")
            or item.get("view_count")
            or item.get("fb_play_count")
        ),
        "likes": item.get("like_count"),
        "comments": item.get("comment_count")
    }
