def classify_question(question: str):

    q = question.lower()

    metadata_words = [
        "engagement rate",
        "creator",
        "title",
        "views",
        "likes",
        "comments",
        "followers",
        "follower count",
        "upload date",
        "duration",
        "hashtags"
    ]

    if any(word in q for word in metadata_words):
        return "metadata"

    comparison_words = [
        "compare",
        "difference",
        "better",
        "engagement",
        "video a",
        "video b",
        "outperform"
    ]

    if any(word in q for word in comparison_words):
        return "comparison"

    return "qa"
