from app.services.comparison_service import answer_comparison


def comparison_node(state):

    result = answer_comparison(
        state["question"],
        state.get("thread_id", "default")
    )

    state["answer"] = result["answer"]
    state["sources"] = result["sources"]

    return state
