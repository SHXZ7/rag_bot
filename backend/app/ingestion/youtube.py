from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

from urllib.parse import urlparse, parse_qs


class YoutubeTranscriptService:

    def get_video_id(self, url):
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]

        parsed = urlparse(url)
        return parse_qs(parsed.query)["v"][0]

    def get_transcript(self, url):

        video_id = self.get_video_id(url)

        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)

            return " ".join(
                item.text
                for item in transcript
            )
        except TranscriptsDisabled:
            return "Transcripts not available for this video"
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise


youtube_service = YoutubeTranscriptService()
