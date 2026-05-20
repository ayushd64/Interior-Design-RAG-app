# src/vector_db/pinecone_repo.py
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from src.vector_db.base import VectorDBRepository
from src.embeddings import get_embeddings
from typing import List, Any, Optional
from dotenv import load_dotenv
import os
import time
import uuid

load_dotenv()

# ─────────────────────────────────────────────────
# Custom Pinecone Retriever for LangChain
# ─────────────────────────────────────────────────
class PineconeRetriever(BaseRetriever):
    """Custom LangChain retriever for Pinecone"""
    
    pinecone_repo: Any = None
    k            : int = 4
    
    def _get_relevant_documents(
        self, 
        query  : str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self.pinecone_repo.search(query, k=self.k)

# ─────────────────────────────────────────────────
# Pinecone Implementation
# ─────────────────────────────────────────────────
class PineconeRepository(VectorDBRepository):
    """
    Pinecone implementation of VectorDBRepository
    Uses Pinecone SDK directly!
    """
    
    def __init__(self):
        self.pc          = None
        self.index       = None
        self.embeddings  = None
        
        self.api_key     = os.getenv("PINECONE_API_KEY")
        self.index_name  = os.getenv(
            "PINECONE_INDEX_NAME",
            "interior-design-rag"
        )
        self.cloud       = os.getenv("PINECONE_CLOUD", "aws")
        self.region      = os.getenv("PINECONE_REGION", "us-east-1")
        
        # ── Dimensions for all-MiniLM-L6-v2 ───────
        self.dimensions = 384
    
    # ── Connection Methods ────────────────────────
    async def connect(self) -> None:
        """Initialize Pinecone connection"""
        print(f"🔍 Connecting to Pinecone...")
        print(f"   Index: {self.index_name}")
        
        try:
            # ── Validate API Key ──────────────────
            if not self.api_key:
                raise ValueError(
                    "PINECONE_API_KEY not set in .env!"
                )
            
            # ── Initialize Pinecone Client ────────
            self.pc = Pinecone(api_key=self.api_key)
            
            # ── Get Embeddings ────────────────────
            self.embeddings = get_embeddings()
            
            # ── Check If Index Exists ─────────────
            existing_indexes = [
                idx.name for idx in self.pc.list_indexes()
            ]
            
            if self.index_name not in existing_indexes:
                print(f"⚠️ Index '{self.index_name}' not found")
                print(f"   Creating new index...")
                
                # ── Create Index ──────────────────
                self.pc.create_index(
                    name      = self.index_name,
                    dimension = self.dimensions,
                    metric    = "cosine",
                    spec      = ServerlessSpec(
                        cloud  = self.cloud,
                        region = self.region
                    )
                )
                
                # ── Wait For Index To Be Ready ────
                print(f"   Waiting for index to be ready...")
                while not self.pc.describe_index(
                    self.index_name
                ).status["ready"]:
                    time.sleep(1)
                
                print(f"✅ Index created!")
            else:
                print(f"✅ Index '{self.index_name}' already exists")
            
            # ── Get Index Reference ───────────────
            self.index = self.pc.Index(self.index_name)
            
            print("✅ Pinecone connected successfully!")
            
            # ── Show Stats ────────────────────────
            stats = self.index.describe_index_stats()
            total = stats.get("total_vector_count", 0)
            print(f"   Total vectors: {total}")
            
        except Exception as e:
            print(f"❌ Pinecone connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Pinecone connection"""
        self.index       = None
        self.pc          = None
        print("✅ Pinecone connection closed!")
    
    # ── Vector Operations ─────────────────────────
    def add_documents(
        self, 
        documents: List[Document]
    ) -> None:
        """Add documents to Pinecone"""
        if not self.index:
            raise RuntimeError("Pinecone not connected!")
        
        print(f"   Embedding {len(documents)} documents...")
        
        # ── Embed All Documents ───────────────────
        texts      = [doc.page_content for doc in documents]
        embeddings = self.embeddings.embed_documents(texts)
        
        # ── Prepare Vectors For Pinecone ──────────
        vectors = []
        for i, (doc, embedding) in enumerate(
            zip(documents, embeddings)
        ):
            vector_id = str(uuid.uuid4())
            
            # Metadata stores the actual text!
            metadata = {
                "text": doc.page_content,
                **(doc.metadata or {})
            }
            
            vectors.append({
                "id"      : vector_id,
                "values"  : embedding,
                "metadata": metadata
            })
        
        # ── Upload In Batches (Pinecone limit) ────
        batch_size = 100
        total_batches = (len(vectors) + batch_size - 1) // batch_size
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"   Uploading batch {batch_num}/{total_batches}...")
            self.index.upsert(vectors=batch)
        
        print(f"✅ Added {len(documents)} documents to Pinecone")
    
    def search(
        self,
        query: str,
        k    : int = 4
    ) -> List[Document]:
        """Search for similar documents"""
        if not self.index:
            raise RuntimeError("Pinecone not connected!")
        
        # ── Embed Query ───────────────────────────
        query_embedding = self.embeddings.embed_query(query)
        
        # ── Search Pinecone ───────────────────────
        results = self.index.query(
            vector          = query_embedding,
            top_k           = k,
            include_metadata= True
        )
        
        # ── Convert Results To Documents ──────────
        documents = []
        for match in results.matches:
            metadata = match.metadata or {}
            text = metadata.pop("text", "")
            
            documents.append(Document(
                page_content = text,
                metadata     = metadata
            ))
        
        return documents
    
    def get_retriever(self) -> Any:
        """Get LangChain retriever"""
        if not self.index:
            raise RuntimeError("Pinecone not connected!")
        
        return PineconeRetriever(
            pinecone_repo = self,
            k             = 4
        )
    
    def delete_all(self) -> None:
        """Delete all vectors in index"""
        if not self.index:
            raise RuntimeError("Pinecone not connected!")
        
        self.index.delete(delete_all=True)
        print("✅ All Pinecone vectors deleted")
    
    def count(self) -> int:
        """Count vectors in index"""
        if not self.index:
            raise RuntimeError("Pinecone not connected!")
        
        stats = self.index.describe_index_stats()
        return stats.get("total_vector_count", 0)

