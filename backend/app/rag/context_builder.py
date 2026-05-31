def _limit_text(text: str, max_chars: int):
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."


def build_context(
    results,
    max_chars: int = 2500,
    max_doc_chars: int = 900
):

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context = []
    sources = []

    for doc, meta in zip(
        docs,
        metas
    ):
        if sum(len(item) for item in context) >= max_chars:
            break

        context.append(
            f"""
VIDEO {meta["video_id"]}

{_limit_text(doc, max_doc_chars)}
"""
        )

        sources.append(
            {
                "video_id": meta["video_id"],
                "chunk_id": meta["chunk_id"],
                "creator": meta.get("creator"),
                "preview": doc[:150]
            }
        )

    return _limit_text(
        "\n\n".join(context),
        max_chars
    ), sources
