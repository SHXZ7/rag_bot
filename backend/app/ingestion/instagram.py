import yt_dlp
import tempfile
import os
import shutil

from app.ingestion.cookies import get_cookiefile
from faster_whisper import WhisperModel
from yt_dlp.utils import DownloadError


class InstagramTranscriptService:

    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            # Disable CUDA to avoid cublas64_12.dll issues on Windows
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            self.model = WhisperModel(
                "base",
                device="cpu",
                compute_type="int8"
            )

    def _find_downloaded_file(self, temp_dir):
        files = [
            os.path.join(temp_dir, name)
            for name in os.listdir(temp_dir)
        ]

        files = [
            path
            for path in files
            if os.path.isfile(path)
        ]

        if not files:
            return None

        wav_files = [
            path
            for path in files
            if path.lower().endswith(".wav")
        ]

        if wav_files:
            return max(wav_files, key=os.path.getsize)

        return max(files, key=os.path.getsize)

    def _get_ffmpeg_location(self):
        ffprobe_path = shutil.which("ffprobe")
        if ffprobe_path:
            return os.path.dirname(ffprobe_path)

        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return os.path.dirname(ffmpeg_path)

        return None

    def get_transcript(self, url):

        self._load_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            ffmpeg_location = self._get_ffmpeg_location()
            opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(
                    temp_dir,
                    "%(id)s"
                ),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "wav",
                        "preferredquality": "192"
                    }
                ],
                "noplaylist": True
            }

            if ffmpeg_location:
                opts["ffmpeg_location"] = ffmpeg_location

            cookies_file = get_cookiefile()
            if cookies_file:
                opts["cookiefile"] = cookies_file

            print(f"Downloading Instagram media from: {url}")
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
            except DownloadError as e:
                print(f"Instagram download failed: {e}")
                return "Transcript not available for this Instagram video"

            temp_file = self._find_downloaded_file(temp_dir)
            if temp_file is None:
                print("Instagram download did not produce a media file")
                return "Transcript not available for this Instagram video"

            print(f"Transcribing: {temp_file}")
            segments, _ = self.model.transcribe(
                temp_file
            )

            transcript = " ".join(
                s.text
                for s in segments
            )

        print(f"Transcript length: {len(transcript)} chars")
        print(f"First 200 chars: {transcript[:200]}")

        return transcript


instagram_service = InstagramTranscriptService()
