# src/vector_db/chromadb_repo.py
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.vector_db.base import VectorDBRepository
from src.embeddings import get_embeddings
from typing import List, Any
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# ChromaDB Implementation
# ─────────────────────────────────────────────────
class ChromaDBRepository(VectorDBRepository):
    """
    ChromaDB implementation of VectorDBRepository
    Stores vectors locally - completely free!
    """
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings  = None
        self.chroma_path = os.getenv(
            "CHROMA_DB_PATH",
            "./vectorstore/chromadb"
        )
        self.collection_name = os.getenv(
            "CHROMA_COLLECTION_NAME",
            "interior_design"
        )
    
    # ── Connection Methods ────────────────────────
    async def connect(self) -> None:
        """Initialize ChromaDB connection"""
        print(f"🔍 Connecting to ChromaDB...")
        print(f"   Path: {self.chroma_path}")
        
        try:
            # Get embeddings
            self.embeddings = get_embeddings()
            
            # Initialize vectorstore
            self.vectorstore = Chroma(
                collection_name    = self.collection_name,
                embedding_function = self.embeddings,
                persist_directory  = self.chroma_path
            )
            
            print("✅ ChromaDB connected successfully!")
            print(f"   Collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ ChromaDB connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close ChromaDB connection"""
        # ChromaDB doesn't need explicit closing
        self.vectorstore = None
        print("✅ ChromaDB connection closed!")
    
    # ── Vector Operations ─────────────────────────
    def add_documents(
        self, 
        documents: List[Document]
    ) -> None:
        """Add documents to ChromaDB"""
        if not self.vectorstore:
            raise RuntimeError("ChromaDB not connected!")
        
        self.vectorstore.add_documents(documents)
        print(f"✅ Added {len(documents)} documents to ChromaDB")
    
    def search(
        self,
        query: str,
        k    : int = 4
    ) -> List[Document]:
        """Search for similar documents"""
        if not self.vectorstore:
            raise RuntimeError("ChromaDB not connected!")
        
        return self.vectorstore.similarity_search(
            query, 
            k=k
        )
    
    def get_retriever(self) -> Any:
        """Get LangChain retriever"""
        if not self.vectorstore:
            raise RuntimeError("ChromaDB not connected!")
        
        return self.vectorstore.as_retriever(
            search_type   = "similarity",
            search_kwargs = {"k": 4}
        )
    
    def delete_all(self) -> None:
        """Delete all documents in collection"""
        if not self.vectorstore:
            raise RuntimeError("ChromaDB not connected!")
        
        # Delete and recreate collection
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name    = self.collection_name,
            embedding_function = self.embeddings,
            persist_directory  = self.chroma_path
        )
        print("✅ All ChromaDB documents deleted")
    
    def count(self) -> int:
        """Count documents in collection"""
        if not self.vectorstore:
            raise RuntimeError("ChromaDB not connected!")
        
        return self.vectorstore._collection.count()

