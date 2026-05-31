def calculate_engagement(
    views: int,
    likes: int,
    comments: int
):

    if views == 0:
        return 0

    return round(
        ((likes + comments) / views) * 100,
        2
    )
