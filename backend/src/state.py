# src/state.py
from typing import TypedDict, List, Optional
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    Represents the state of our RAG graph

    Attributes:
        question         : Current user question
        chat_history     : Previous messages
        user_level       : beginner or expert
        documents        : Retrieved documents
        generation       : LLM generated answer
        is_relevant      : Are documents relevant?
        retry_count      : How many times retried
        is_design_related: Is question about design?
    """
    question          : str
    chat_history      : Optional[List[dict]]  # ← New!
    user_level        : Optional[str]
    documents         : Optional[List[Document]]
    generation        : Optional[str]
    is_relevant       : Optional[bool]
    retry_count       : Optional[int]
    is_design_related : Optional[bool]