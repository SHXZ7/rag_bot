from pydantic import BaseModel
from typing import Optional


class IngestRequest(BaseModel):
    video_a_url: str
    video_b_url: str


class VideoData(BaseModel):
    video_id: str

    url: str

    title: Optional[str] = None

    creator: Optional[str] = None

    follower_count: Optional[int] = None

    views: int = 0

    likes: int = 0

    comments: int = 0

    upload_date: Optional[str] = None

    duration: Optional[int] = None

    hashtags: list[str] = []

    transcript: str = ""

    engagement_rate: float = 0.0
