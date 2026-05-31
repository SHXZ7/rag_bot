from app.rag.question_router import route_question
from app.services.comparison_service import build_comparison_prompt
from app.services.qa_service import build_qa_prompt


def get_sources(question, thread_id="default"):

    route = route_question(question)

    if route == "comparison":
        _prompt, sources = build_comparison_prompt(
            question,
            thread_id
        )
        return sources

    if route == "qa":
        _prompt, sources = build_qa_prompt(
            question,
            thread_id
        )
        return sources

    return []
