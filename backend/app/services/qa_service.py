from app.core.chat_history import chat_history
from app.rag.context_builder import build_context
from app.rag.history_builder import build_history
from app.rag.prompts import QA_PROMPT
from app.rag.retriever import retrieve_for_video
from app.services.llm import generate_answer


def build_qa_prompt(
    question,
    thread_id="default"
):

    a = retrieve_for_video(question, "A", k=2)
    b = retrieve_for_video(question, "B", k=2)

    a_context, a_sources = build_context(a)
    b_context, b_sources = build_context(b)
    history_text = build_history(
        chat_history[thread_id]
    )

    prompt = f"""
{QA_PROMPT}

CHAT HISTORY:

{history_text}

CONTEXT:

{a_context}

{b_context}

QUESTION:

{question}
"""

    return prompt, a_sources + b_sources


def answer_qa(
    question,
    thread_id="default"
):

    prompt, sources = build_qa_prompt(
        question,
        thread_id
    )

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources
    }
