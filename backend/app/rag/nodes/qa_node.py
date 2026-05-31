from app.services.qa_service import answer_qa


def qa_node(state):

    result = answer_qa(
        state["question"],
        state.get("thread_id", "default")
    )

    state["answer"] = result["answer"]
    state["sources"] = result["sources"]

    return state
