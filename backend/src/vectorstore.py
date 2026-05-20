# src/vectorstore.py
"""
Backward compatibility layer
Routes calls through vector DB factory
"""
from src.vector_db.factory import get_vector_db

def get_vectorstore():
    """
    Get the active vector store
    Works with any vector DB!
    """
    vector_db = get_vector_db()
    return vector_db.vectorstore

def get_retriever():
    """
    Get retriever from active vector DB
    """
    vector_db = get_vector_db()
    return vector_db.get_retriever()

