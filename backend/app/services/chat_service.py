from app.core.chat_history import chat_history
from app.rag.graph import graph


def answer_question(
    question,
    thread_id="default"
):

    result = graph.invoke(
        {
            "question": question,
            "thread_id": thread_id
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    chat_history[thread_id].append(
        {
            "role": "user",
            "content": question
        }
    )

    chat_history[thread_id].append(
        {
            "role": "assistant",
            "content": result["answer"]
        }
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }
