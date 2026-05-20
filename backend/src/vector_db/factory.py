# src/vector_db/factory.py
from src.vector_db.base import VectorDBRepository
from src.vector_db.chromadb_repo import ChromaDBRepository
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# Vector Database Factory
# ─────────────────────────────────────────────────
_vector_db_instance: VectorDBRepository = None

def get_vector_db_type() -> str:
    """
    Get vector database type from environment
    Default: chromadb
    """
    return os.getenv("VECTOR_DB_TYPE", "chromadb").lower()

async def init_vector_db() -> VectorDBRepository:
    """
    Factory function to create vector DB instance
    based on VECTOR_DB_TYPE env variable
    """
    global _vector_db_instance
    
    db_type = get_vector_db_type()
    
    print(f"\n{'='*50}")
    print(f"🏭 Vector DB Factory: Initializing {db_type.upper()}")
    print(f"{'='*50}\n")
    
    # ── Select Vector DB Implementation ───────────
    if db_type == "chromadb":
        _vector_db_instance = ChromaDBRepository()
    
    elif db_type == "pinecone":
        # Will add in Phase 3!
        try:
            from src.vector_db.pinecone_repo import PineconeRepository
            _vector_db_instance = PineconeRepository()
        except ImportError:
            print("❌ Pinecone not yet implemented!")
            print("   Falling back to ChromaDB")
            _vector_db_instance = ChromaDBRepository()
    
    else:
        print(f"⚠️ Unknown vector DB type: {db_type}")
        print("   Falling back to ChromaDB")
        _vector_db_instance = ChromaDBRepository()
    
    # ── Connect To Vector DB ──────────────────────
    await _vector_db_instance.connect()
    
    return _vector_db_instance

async def close_vector_db() -> None:
    """Close the active vector DB connection"""
    global _vector_db_instance
    
    if _vector_db_instance:
        await _vector_db_instance.disconnect()
        _vector_db_instance = None

def get_vector_db() -> VectorDBRepository:
    """Get the active vector DB instance"""
    if _vector_db_instance is None:
        raise RuntimeError(
            "Vector DB not initialized! "
            "Call init_vector_db() first."
        )
    return _vector_db_instance

