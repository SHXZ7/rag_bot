def route_question(question: str):

    q = question.lower()

    metadata_keywords = [
        "engagement",
        "engagement rate",
        "creator",
        "follower",
        "followers",
        "views",
        "likes",
        "comments",
        "duration",
        "upload date"
    ]

    comparison_keywords = [
        "compare",
        "difference",
        "better",
        "video a",
        "video b",
        "outperform",
        "improvement",
        "improve",
        "hook",
        "which video"
    ]

    if any(k in q for k in metadata_keywords):
        return "metadata"

    if any(k in q for k in comparison_keywords):
        return "comparison"

    return "qa"
