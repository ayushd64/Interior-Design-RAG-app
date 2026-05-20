# src/vector_db/base.py
from abc import ABC, abstractmethod
from typing import List, Any
from langchain_core.documents import Document

# ─────────────────────────────────────────────────
# Abstract Vector Database Interface
# ─────────────────────────────────────────────────
class VectorDBRepository(ABC):
    """
    Abstract base class for vector database implementations
    
    Any vector DB (ChromaDB, Pinecone, etc.) must
    implement ALL these methods!
    """
    
    # ── Connection Methods ────────────────────────
    @abstractmethod
    async def connect(self) -> None:
        """Initialize vector database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close vector database connection"""
        pass
    
    # ── Vector Operations ─────────────────────────
    @abstractmethod
    def add_documents(
        self, 
        documents: List[Document]
    ) -> None:
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        k    : int = 4
    ) -> List[Document]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def get_retriever(self) -> Any:
        """Get LangChain retriever interface"""
        pass
    
    @abstractmethod
    def delete_all(self) -> None:
        """Delete all documents"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count number of documents"""
        pass

