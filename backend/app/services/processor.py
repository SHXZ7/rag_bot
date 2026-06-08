from app.ingestion.url_parser import (
    detect_platform
)

from app.ingestion.metadata import (
    metadata_extractor
)

from app.ingestion.youtube import (
    youtube_service
)

from app.ingestion.instagram import (
    instagram_service
)

from app.ingestion.utils import (
    extract_hashtags
)

from app.services.engagement import (
    calculate_engagement
)


import os
import tempfile
from pathlib import Path

class VideoProcessor:

    async def process(
        self,
        url: str,
        video_id: str,
        cookies_yt: str = None,
        cookies_ig: str = None
    ):

        platform = detect_platform(url)
        cookie_file_path = None

        try:
            raw_cookies = cookies_yt if platform == "youtube" else cookies_ig
            if raw_cookies:
                # Use delete=False for compatibility on Windows where files cannot
                # easily be opened in other processes if already locked.
                tf = tempfile.NamedTemporaryFile(
                    mode="w",
                    delete=False,
                    suffix=".txt",
                    encoding="utf-8"
                )
                tf.write(raw_cookies.strip())
                tf.close()
                cookie_file_path = tf.name
                print(f"[processor] Created temporary cookie file for {platform}: {cookie_file_path}")

            metadata = (
                metadata_extractor.extract(url, cookie_file=cookie_file_path)
            )

            if platform == "youtube":
                transcript = (
                    youtube_service
                    .get_transcript(url, cookie_file=cookie_file_path)
                )
            else:
                transcript = (
                    instagram_service
                    .get_transcript(url, cookie_file=cookie_file_path)
                )

        finally:
            if cookie_file_path and os.path.exists(cookie_file_path):
                try:
                    os.unlink(cookie_file_path)
                    print(f"[processor] Cleaned up temporary cookie file: {cookie_file_path}")
                except Exception as e:
                    print(f"[processor] Failed to clean up temp cookie file {cookie_file_path}: {e}")

        engagement_rate = (
            calculate_engagement(
                metadata["views"],
                metadata["likes"],
                metadata["comments"]
            )
        )

        return {
            "video_id": video_id,
            "url": url,

            **metadata,

            "hashtags": extract_hashtags(
                metadata.get(
                    "description",
                    ""
                )
            ),

            "transcript": transcript,

            "engagement_rate": engagement_rate
        }


processor = VideoProcessor()
