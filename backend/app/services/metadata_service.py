from app.core.chat_history import chat_history
from app.core.video_store import video_store


def _format_count(value):
    if value is None:
        return "unavailable"

    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def _creator_and_followers(video_id, video):
    return (
        f"Video {video_id} creator: {video.get('creator') or 'unavailable'}. "
        f"Follower count: {_format_count(video.get('follower_count'))}."
    )


def _infer_video_id(question, thread_id):
    q = question.lower()

    if "video a" in q:
        return "A"

    if "video b" in q:
        return "B"

    pronouns = [
        "their",
        "that",
        "it",
        "its"
    ]

    if not any(word in q for word in pronouns):
        return None

    for msg in reversed(chat_history[thread_id][-6:]):
        content = msg["content"].lower()

        if "video b" in content or "creator b" in content:
            return "B"

        if "video a" in content or "creator a" in content:
            return "A"

    return None


def answer_metadata_question(
    question: str,
    thread_id="default"
):

    a = video_store.get("A", {})
    b = video_store.get("B", {})

    q = question.lower()
    video_id = _infer_video_id(
        question,
        thread_id
    )

    # Engagement-specific questions
    if "engagement" in q:
        if video_id == "A":
            return {
                "answer": (
                    f"**Summary**: Video A engagement rate is {a.get('engagement_rate', 0)}%.\n\n"
                    f"**Details**:\n- Engagement rate: {a.get('engagement_rate', 0)}%\n- Views: {_format_count(a.get('views'))}\n- Likes: {_format_count(a.get('likes'))}\n- Comments: {_format_count(a.get('comments'))}\n\n"
                    f"**Sources**: VIDEO A METADATA"
                ),
                "sources": []
            }

        if video_id == "B":
            return {
                "answer": (
                    f"**Summary**: Video B engagement rate is {b.get('engagement_rate', 0)}%.\n\n"
                    f"**Details**:\n- Engagement rate: {b.get('engagement_rate', 0)}%\n- Views: {_format_count(b.get('views'))}\n- Likes: {_format_count(b.get('likes'))}\n- Comments: {_format_count(b.get('comments'))}\n\n"
                    f"**Sources**: VIDEO B METADATA"
                ),
                "sources": []
            }

        return {
            "answer": (
                f"**Summary**: Video A {a.get('engagement_rate', 0)}% — Video B {b.get('engagement_rate', 0)}%.\n\n"
                f"**Details**:\n- Video A: {a.get('engagement_rate', 0)}% (Views: {_format_count(a.get('views'))}, Likes: {_format_count(a.get('likes'))}, Comments: {_format_count(a.get('comments'))})\n- Video B: {b.get('engagement_rate', 0)}% (Views: {_format_count(b.get('views'))}, Likes: {_format_count(b.get('likes'))}, Comments: {_format_count(b.get('comments'))})\n\n"
                f"**Sources**: VIDEO A METADATA; VIDEO B METADATA"
            ),
            "sources": []
        }

    # Creator / follower questions
    if "follower" in q or "followers" in q or "creator" in q:
        if video_id == "A":
            return {
                "answer": (
                    f"**Summary**: Creator information for Video A.\n\n"
                    f"**Details**:\n- Creator: {a.get('creator') or 'unavailable'}\n- Follower count: {_format_count(a.get('follower_count'))}\n\n"
                    f"**Sources**: VIDEO A METADATA"
                ),
                "sources": []
            }

        if video_id == "B":
            return {
                "answer": (
                    f"**Summary**: Creator information for Video B.\n\n"
                    f"**Details**:\n- Creator: {b.get('creator') or 'unavailable'}\n- Follower count: {_format_count(b.get('follower_count'))}\n\n"
                    f"**Sources**: VIDEO B METADATA"
                ),
                "sources": []
            }

        return {
            "answer": (
                f"**Summary**: Creator information for both videos.\n\n"
                f"**Details**:\n- Video A: {a.get('creator') or 'unavailable'} — Followers: {_format_count(a.get('follower_count'))}\n- Video B: {b.get('creator') or 'unavailable'} — Followers: {_format_count(b.get('follower_count'))}\n\n"
                f"**Sources**: VIDEO A METADATA; VIDEO B METADATA"
            ),
            "sources": []
        }

    return {
        "answer": "Metadata available but question not recognized.",
        "sources": []
    }
