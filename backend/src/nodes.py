# src/nodes.py
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from src.state import GraphState
from src.prompts import (
    CLASSIFY_PROMPT,
    GRADE_PROMPT,
    BEGINNER_PROMPT,
    EXPERT_PROMPT,
    HALLUCINATION_PROMPT,
    REPHRASE_PROMPT,
    TOPIC_GUARD_PROMPT
)
from src.vectorstore import get_retriever
from dotenv import load_dotenv
import os

load_dotenv()

# ── Initialize LLM ────────────────────────────────
llm = ChatOllama(
    base_url   = os.getenv("OLLAMA_BASE_URL", 
                           "http://127.0.0.1:11434"),
    model      = os.getenv("OLLAMA_MODEL", 
                           "llama3.1:8b"),
    temperature= 0.7
)

# ── Initialize Retriever ──────────────────────────
# ── Lazy Retriever Initialization ─────────────────
_retriever = None

def _get_retriever():
    """Lazy load retriever after vector DB initialized"""
    global _retriever
    if _retriever is None:
        _retriever = get_retriever()
    return _retriever



# ── Output Parser ─────────────────────────────────
parser = StrOutputParser()

# ── Format Chat History Helper ────────────────────
def format_chat_history(chat_history: list) -> str:
    """
    Format chat history list into readable string
    for the LLM prompt
    """
    if not chat_history:
        return "No previous conversation."

    formatted = []
    for msg in chat_history:
        role    = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            formatted.append(f"User: {content}")
        elif role == "assistant":
            formatted.append(f"Assistant: {content}")

    return "\n".join(formatted)

# ─────────────────────────────────────────────────
# NODE 0 - Topic Guard
# ─────────────────────────────────────────────────
def topic_guard_node(state: GraphState) -> GraphState:
    """
    Check if question is related to interior design
    """
    print("--- NODE: Checking Topic Relevance ---")

    question = state["question"]

    chain  = TOPIC_GUARD_PROMPT | llm | parser
    result = chain.invoke({"question": question})

    is_design_related = "YES" in result.strip().upper()

    print(f"--- Is Design Related: {is_design_related} ---")

    if not is_design_related:
        rejection = """I'm specialized in interior design only! 🏠

I cannot help with that topic. But I'd love to help you with:

- 🛋️ **Room decoration ideas**
- 🎨 **Color schemes and palettes**
- 💡 **Lighting design tips**
- 🪑 **Furniture arrangement**
- 🏛️ **Design styles and history**
- 📐 **Space planning**

What would you like to know about interior design?"""

        return {
            **state,
            "generation" : rejection,
            "is_relevant": False,
            "user_level" : "BEGINNER"
        }

    return {**state, "is_relevant": True}

# ─────────────────────────────────────────────────
# NODE 1 - Classify User Level
# ─────────────────────────────────────────────────
def classify_node(state: GraphState) -> GraphState:
    """
    Classify if user is BEGINNER or EXPERT
    """
    print("--- NODE: Classifying User level ---")

    question = state["question"]

    chain      = CLASSIFY_PROMPT | llm | parser
    result     = chain.invoke({"question": question})
    user_level = result.strip().upper()

    if "EXPERT" in user_level:
        user_level = "EXPERT"
    else:
        user_level = "BEGINNER"

    print(f"--- User Level: {user_level} ---")

    return {**state, "user_level": user_level}

# ─────────────────────────────────────────────────
# NODE 2 - Retrieve Documents
# ─────────────────────────────────────────────────
def retrieve_node(state: GraphState) -> GraphState:
    """
    Retrieve relevant documents from ChromaDB
    """
    print("--- NODE: Retrieving documents ---")

    question  = state["question"]
    documents = _get_retriever().invoke(question)

    print(f"--- Retrieved {len(documents)} documents ---")

    return {**state, "documents": documents}

# ─────────────────────────────────────────────────
# NODE 3 - Grade Documents
# ─────────────────────────────────────────────────
def grade_node(state: GraphState) -> GraphState:
    """
    Check if retrieved documents are relevant
    """
    print("--- NODE: Grading documents ---")

    question  = state["question"]
    documents = state["documents"]

    docs_text = "\n\n".join([
        doc.page_content for doc in documents
    ])

    chain  = GRADE_PROMPT | llm | parser
    result = chain.invoke({
        "question" : question,
        "documents": docs_text
    })

    is_relevant = "YES" in result.strip().upper()

    print(f"--- Documents Relevant: {is_relevant} ---")

    return {**state, "is_relevant": is_relevant}

# ─────────────────────────────────────────────────
# NODE 4 - Generate Answer (With Memory!)
# ─────────────────────────────────────────────────
def generate_node(state: GraphState) -> GraphState:
    """
    Generate answer based on user level
    NOW includes chat history for context!
    """
    print("--- NODE: Generating Answer ---")

    question     = state["question"]
    documents    = state["documents"]
    user_level   = state["user_level"]
    chat_history = state.get("chat_history", [])

    # ── Format context from documents ────────────
    context = "\n\n".join([
        doc.page_content for doc in documents
    ])

    # ── Format chat history for prompt ───────────
    formatted_history = format_chat_history(chat_history)

    # ── Choose prompt based on user level ────────
    if user_level == "EXPERT":
        prompt = EXPERT_PROMPT
        print("--- Using Expert prompt ---")
    else:
        prompt = BEGINNER_PROMPT
        print("--- Using Beginner prompt ---")

    chain      = prompt | llm | parser
    generation = chain.invoke({
        "question"    : question,
        "context"     : context,
        "chat_history": formatted_history  # ← Memory!
    })

    print("--- Answer Generated ---")

    return {**state, "generation": generation}

# ─────────────────────────────────────────────────
# NODE 5 - Check Hallucination
# ─────────────────────────────────────────────────
def hallucination_node(state: GraphState) -> GraphState:
    """
    Check if generated answer is grounded
    """
    print("--- NODE: Checking Hallucination ---")

    documents  = state["documents"]
    generation = state["generation"]

    context = "\n\n".join([
        doc.page_content for doc in documents
    ])

    chain      = HALLUCINATION_PROMPT | llm | parser
    result     = chain.invoke({
        "context"   : context,
        "generation": generation
    })

    is_grounded = "YES" in result.strip().upper()

    print(f"--- Answer Grounded: {is_grounded} ---")

    return {**state, "is_relevant": is_grounded}

# ─────────────────────────────────────────────────
# NODE 6 - Rephrase Question
# ─────────────────────────────────────────────────
def rephrase_node(state: GraphState) -> GraphState:
    """
    Rephrase question if documents not relevant
    """
    print("--- NODE: Rephrasing Question ---")

    question    = state["question"]
    retry_count = state.get("retry_count", 0)

    chain     = REPHRASE_PROMPT | llm | parser
    rephrased = chain.invoke({"question": question})
    rephrased = rephrased.strip()

    print(f"--- Rephrased: {rephrased} ---")

    return {
        **state,
        "question"   : rephrased,
        "retry_count": retry_count + 1
    }