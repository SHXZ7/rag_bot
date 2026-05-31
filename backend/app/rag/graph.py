from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.rag.nodes.comparison_node import comparison_node
from app.rag.nodes.metadata_node import metadata_node
from app.rag.nodes.qa_node import qa_node
from app.rag.nodes.router_node import router_node
from app.rag.state import GraphState


def choose_route(state):

    return state["route"]


builder = StateGraph(GraphState)

builder.add_node(
    "router",
    router_node
)

builder.add_node(
    "qa",
    qa_node
)

builder.add_node(
    "metadata",
    metadata_node
)

builder.add_node(
    "comparison",
    comparison_node
)

builder.set_entry_point(
    "router"
)

builder.add_conditional_edges(
    "router",
    choose_route,
    {
        "qa": "qa",
        "metadata": "metadata",
        "comparison": "comparison"
    }
)

builder.add_edge(
    "qa",
    END
)

builder.add_edge(
    "metadata",
    END
)

builder.add_edge(
    "comparison",
    END
)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)
