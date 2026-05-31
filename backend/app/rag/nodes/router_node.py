from app.rag.question_router import route_question


def router_node(state):

    state["route"] = route_question(
        state["question"]
    )

    return state
