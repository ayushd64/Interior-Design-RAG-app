from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.nodes import (
    topic_guard_node,     # ← Add this!
    classify_node,
    retrieve_node,
    grade_node,
    generate_node,
    hallucination_node,
    rephrase_node
)

# ─────────────────────────────────────────────────
# CONDITIONAL EDGES
# ─────────────────────────────────────────────────

# ── New! Topic Guard Decision ─────────────────────
def should_continue(state: GraphState) -> str:
    """
    After topic guard check:
    → If design related    → Continue to classify
    → If not design related → End immediately
    """
    if state.get("is_relevant") == False and \
       state.get("generation") is not None:
        print("--- DECISION: Off topic → End ---")
        return "end"
    else:
        print("--- DECISION: On topic → Continue ---")
        return "classify"

def should_rephrase(state: GraphState) -> str:
    """
    After grading documents:
    → If relevant     → Generate answer
    → If not relevant → Rephrase (max 2 retries)
    """
    retry_count = state.get("retry_count", 0)

    if state["is_relevant"]:
        print("--- DECISION: Documents relevant → Generate ---")
        return "generate"
    elif retry_count >= 2:
        print("--- DECISION: Max retries reached → Generate anyway ---")
        return "generate"
    else:
        print("--- DECISION: Not relevant → Rephrase ---")
        return "rephrase"

def check_hallucination(state: GraphState) -> str:
    """
    After generating answer:
    → If grounded      → End
    → If hallucinating → Regenerate (max 2 retries)
    """
    retry_count = state.get("retry_count", 0)

    if state["is_relevant"]:
        print("--- DECISION: Answer grounded → End ---")
        return "end"
    elif retry_count >= 2:
        print("--- DECISION: Max retries → End anyway ---")
        return "end"
    else:
        print("--- DECISION: Hallucinating → Regenerate ---")
        return "regenerate"

# ─────────────────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────────────────
def build_graph():
    """
    Build and compile LangGraph RAG pipeline
    """
    # Initialize graph
    graph = StateGraph(GraphState)

    # ── Add Nodes ─────────────────────────────────
    graph.add_node("topic_guard" , topic_guard_node)  # ← New!
    graph.add_node("classify"    , classify_node)
    graph.add_node("retrieve"    , retrieve_node)
    graph.add_node("grade"       , grade_node)
    graph.add_node("generate"    , generate_node)
    graph.add_node("hallucination", hallucination_node)
    graph.add_node("rephrase"    , rephrase_node)

    # ── Add Edges ─────────────────────────────────
    # Start → Topic Guard
    graph.set_entry_point("topic_guard")

    # Topic Guard → (Classify or End)
    graph.add_conditional_edges(
        "topic_guard",
        should_continue,
        {
            "classify" : "classify",
            "end"      : END          # ← Reject here!
        }
    )

    # Classify → Retrieve
    graph.add_edge("classify", "retrieve")

    # Retrieve → Grade
    graph.add_edge("retrieve", "grade")

    # Grade → (Rephrase or Generate)
    graph.add_conditional_edges(
        "grade",
        should_rephrase,
        {
            "generate" : "generate",
            "rephrase" : "rephrase"
        }
    )

    # Rephrase → Retrieve (retry)
    graph.add_edge("rephrase", "retrieve")

    # Generate → Hallucination Check
    graph.add_edge("generate", "hallucination")

    # Hallucination → (End or Regenerate)
    graph.add_conditional_edges(
        "hallucination",
        check_hallucination,
        {
            "end"       : END,
            "regenerate": "generate"
        }
    )

    # ── Compile Graph ─────────────────────────────
    app = graph.compile()
    print("✅ LangGraph pipeline compiled successfully!")
    return app

# ── Singleton Graph Instance ──────────────────────
rag_graph = build_graph()