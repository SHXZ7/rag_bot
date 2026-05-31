# pyrefly: ignore [missing-import]
from youtube_transcript_api import YouTubeTranscriptApi
# pyrefly: ignore [missing-import]
from youtube_transcript_api._errors import TranscriptsDisabled, IpBlocked

import os
import re
import tempfile
from urllib.parse import urlparse, parse_qs

import yt_dlp

from app.ingestion.cookies import get_youtube_cookiefile


class YoutubeTranscriptService:

    def get_video_id(self, url: str) -> str:
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        parsed = urlparse(url)
        return parse_qs(parsed.query)["v"][0]

    def get_transcript(self, url: str) -> str:
        video_id = self.get_video_id(url)
        cookies_file = get_youtube_cookiefile()

        if cookies_file:
            print(f"[youtube] Using cookies: {cookies_file}")
        else:
            print("[youtube] WARNING: No YouTube cookies file found.")

        # ── Strategy 1: yt-dlp subtitle download (cookies already work here) ──
        if cookies_file:
            try:
                text = self._fetch_via_ytdlp(url, cookies_file)
                if text:
                    print(f"[youtube] yt-dlp subtitles OK ({len(text)} chars)")
                    return text
                print("[youtube] yt-dlp returned no subtitle text, trying transcript-api…")
            except Exception as e:
                print(f"[youtube] yt-dlp subtitle extraction failed ({type(e).__name__}): {e}")

        # ── Strategy 2: youtube-transcript-api with cookies ──────────────────
        try:
            return self._fetch_via_transcript_api(video_id, cookies_file)
        except TranscriptsDisabled:
            return "Transcripts not available for this video"
        except Exception as e:
            print(f"[youtube] All transcript strategies failed: {type(e).__name__}: {e}")
            return "Could not retrieve transcript for this video"

    # ── yt-dlp subtitle extraction ────────────────────────────────────────────

    def _fetch_via_ytdlp(self, url: str, cookies_file: str) -> str:
        """Download auto/manual subtitles via yt-dlp and return plain text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "writesubtitles": True,       # manual captions
                "writeautomaticsub": True,    # auto-generated captions
                "subtitleslangs": ["en", "en-US", "en-GB", "en-IN"],
                "subtitlesformat": "vtt/srt/best",
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookies_file,
                "outtmpl": os.path.join(tmpdir, "sub"),
                "ignore_no_formats_error": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Pick up the first subtitle file written
            for fname in sorted(os.listdir(tmpdir)):
                fpath = os.path.join(tmpdir, fname)
                if fname.endswith(".vtt"):
                    return self._parse_vtt(fpath)
                if fname.endswith(".srt"):
                    return self._parse_srt(fpath)

        return ""

    @staticmethod
    def _parse_vtt(path: str) -> str:
        """Convert a WebVTT file to deduplicated plain text."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        seen: set[str] = set()
        parts: list[str] = []

        for line in content.splitlines():
            line = line.strip()
            # Skip VTT headers, timestamps, blank lines
            if (not line
                    or line.startswith("WEBVTT")
                    or line.startswith("NOTE")
                    or "-->" in line
                    or re.match(r"^\d+$", line)):
                continue
            # Strip HTML / VTT tags  e.g. <c>, <00:00:01.234>
            clean = re.sub(r"<[^>]+>", "", line).strip()
            if clean and clean not in seen:
                seen.add(clean)
                parts.append(clean)

        return " ".join(parts)

    @staticmethod
    def _parse_srt(path: str) -> str:
        """Convert an SRT file to plain text."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Remove sequence numbers and timestamps
        content = re.sub(r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n", "", content)
        content = re.sub(r"<[^>]+>", "", content)
        return " ".join(content.split())

    # ── youtube-transcript-api fallback ──────────────────────────────────────

    def _fetch_via_transcript_api(self, video_id: str, cookies_file: str | None) -> str:
        """Try youtube-transcript-api; with cookies first, then without."""
        if cookies_file:
            try:
                api = YouTubeTranscriptApi(cookies=cookies_file)
                transcript = api.fetch(video_id)
                return " ".join(item.text for item in transcript)
            except IpBlocked:
                print("[youtube] transcript-api IpBlocked even with cookies.")
            except Exception as e:
                print(f"[youtube] transcript-api (with cookies) failed: {type(e).__name__}: {e}")

        # Last resort — unauthenticated (works if IP isn't blocked)
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        return " ".join(item.text for item in transcript)


youtube_service = YoutubeTranscriptService()
