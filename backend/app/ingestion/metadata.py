import yt_dlp

from app.ingestion.cookies import get_cookiefile_for_url
from app.ingestion.instagram_web import (
    fetch_media_metadata,
    fetch_profile_metadata
)


class MetadataExtractor:

    def extract(self, url: str):

        cookies_file = get_cookiefile_for_url(url)

        opts = {
            "quiet": True,
            "no_warnings": False,
            "skip_download": True,
            "noplaylist": True,
            # We only want metadata — accept any available format and never
            # crash if a specific format is missing.
            "format": "bestaudio/best",
            "ignore_no_formats_error": True,
        }


        if cookies_file:
            print(f"[metadata] Using cookies file: {cookies_file}")
            opts["cookiefile"] = cookies_file
        else:
            print("[metadata] WARNING: No cookies file found — YouTube requests may be blocked.")

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            stats = info.get("statistics") or {}

            views = (
                info.get("view_count")
                or info.get("play_count")
                or info.get("ig_play_count")
                or info.get("views")
                or stats.get("view_count")
                or 0
            )

            username = (
                info.get("channel")
                or info.get("uploader_id")
            )

            profile_metadata = {}
            media_metadata = {}
            try:
                profile_metadata = fetch_profile_metadata(username)
            except Exception as e:
                print(f"Instagram profile metadata fallback failed: {e}")

            try:
                media_metadata = fetch_media_metadata(url, info)
            except Exception as e:
                print(f"Instagram media metadata fallback failed: {e}")

            return {
                "title": info.get("title"),
                "creator": (
                    info.get("uploader")
                    or profile_metadata.get("creator")
                ),
                "follower_count": (
                    info.get("channel_follower_count")
                    or info.get("channel_follower_count_approx")
                    or info.get("uploader_follower_count")
                    or info.get("follower_count")
                    or stats.get("follower_count")
                    or profile_metadata.get("follower_count")
                ),
                "views": media_metadata.get("views") or views,
                "likes": (
                    media_metadata.get("likes")
                    or info.get("like_count", 0)
                ),
                "comments": (
                    media_metadata.get("comments")
                    or info.get("comment_count", 0)
                ),
                "upload_date": info.get("upload_date"),
                "duration": info.get("duration", 0),
                "description": info.get("description", "")
            }


metadata_extractor = MetadataExtractor()
