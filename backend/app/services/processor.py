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


class VideoProcessor:

    async def process(
        self,
        url: str,
        video_id: str
    ):

        platform = detect_platform(url)

        metadata = (
            metadata_extractor.extract(url)
        )

        if platform == "youtube":

            transcript = (
                youtube_service
                .get_transcript(url)
            )

        else:

            transcript = (
                instagram_service
                .get_transcript(url)
            )

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
