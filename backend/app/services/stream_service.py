from app.core.chat_history import chat_history
from app.rag.question_router import route_question
from app.services.comparison_service import build_comparison_prompt
from app.services.llm import stream_answer
from app.services.metadata_service import answer_metadata_question
from app.services.qa_service import build_qa_prompt


def _save_turn(thread_id, question, answer):
    chat_history[thread_id].append(
        {
            "role": "user",
            "content": question
        }
    )

    chat_history[thread_id].append(
        {
            "role": "assistant",
            "content": answer
        }
    )


def stream_question(
    question,
    thread_id="default"
):

    route = route_question(question)

    if route == "metadata":
        result = answer_metadata_question(
            question,
            thread_id
        )
        answer = result["answer"]
        yield answer
        _save_turn(
            thread_id,
            question,
            answer
        )
        return

    if route == "comparison":
        prompt, _sources = build_comparison_prompt(
            question,
            thread_id
        )
    else:
        prompt, _sources = build_qa_prompt(
            question,
            thread_id
        )

    chunks = []

    for delta in stream_answer(prompt):
        chunks.append(delta)
        yield delta

    _save_turn(
        thread_id,
        question,
        "".join(chunks)
    )
