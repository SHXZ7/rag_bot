from typing import TypedDict


class GraphState(TypedDict):
    question: str
    thread_id: str
    route: str
    answer: str
    sources: list
