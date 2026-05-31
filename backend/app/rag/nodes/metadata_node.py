from app.services.metadata_service import answer_metadata_question


def metadata_node(state):

    result = answer_metadata_question(
        state["question"],
        state.get("thread_id", "default")
    )

    state["answer"] = result["answer"]
    state["sources"] = result["sources"]

    return state
