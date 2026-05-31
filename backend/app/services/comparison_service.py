import json

from app.core.video_store import video_store
from app.rag.context_builder import build_context
from app.rag.prompts import COMPARISON_PROMPT
from app.rag.retriever import retrieve_for_video
from app.services.llm import generate_answer


def _metadata_for_prompt(video):
    metadata = {
        key: value
        for key, value in video.items()
        if key != "transcript"
    }

    if "description" in metadata:
        metadata["description"] = str(
            metadata["description"]
        )[:500]

    return json.dumps(
        metadata,
        indent=2,
        default=str
    )


def build_comparison_prompt(
    question,
    thread_id="default"
):

    a_results = retrieve_for_video(question, "A", k=2)
    b_results = retrieve_for_video(question, "B", k=2)

    a_context, a_sources = build_context(a_results)
    b_context, b_sources = build_context(b_results)

    metadata_a = _metadata_for_prompt(video_store["A"])
    metadata_b = _metadata_for_prompt(video_store["B"])

    transcript_a = video_store["A"].get("transcript") or ""
    transcript_b = video_store["B"].get("transcript") or ""

    transcript_status = f"A={len(transcript_a)} chars, B={len(transcript_b)} chars"

    prompt = f"""
{COMPARISON_PROMPT}

VIDEO A METADATA:
{metadata_a}

VIDEO B METADATA:
{metadata_b}

TRANSCRIPT STATUS:
{transcript_status}

VIDEO A CONTEXT:
{a_context}

VIDEO B CONTEXT:
{b_context}

QUESTION:
{question}
"""

    return prompt, a_sources + b_sources


def answer_comparison(
    question,
    thread_id="default"
):

    prompt, sources = build_comparison_prompt(
        question,
        thread_id
    )

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources
    }
