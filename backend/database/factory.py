# database/factory.py
from database.base import DatabaseRepository
from database.mongodb_repo import MongoDBRepository
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# Database Factory
# ─────────────────────────────────────────────────
# Stores the active database instance
_db_instance: DatabaseRepository = None

def get_database_type() -> str:
    """
    Get database type from environment
    Default: mongodb
    """
    return os.getenv("DATABASE_TYPE", "mongodb").lower()

async def init_database() -> DatabaseRepository:
    """
    Factory function to create database instance
    based on DATABASE_TYPE env variable
    
    Returns:
        DatabaseRepository: Connected database instance
    """
    global _db_instance
    
    db_type = get_database_type()
    
    print(f"\n{'='*50}")
    print(f"🏭 Database Factory: Initializing {db_type.upper()}")
    print(f"{'='*50}\n")
    
    # ── Select Database Implementation ────────────
    if db_type == "mongodb":
        _db_instance = MongoDBRepository()
    
    elif db_type == "firestore":
        # Will add in Phase 3!
        try:
            from database.firestore_repo import FirestoreRepository
            _db_instance = FirestoreRepository()
        except ImportError:
            print("❌ Firestore not yet implemented!")
            print("   Falling back to MongoDB")
            _db_instance = MongoDBRepository()
    
    else:
        print(f"⚠️ Unknown database type: {db_type}")
        print("   Falling back to MongoDB")
        _db_instance = MongoDBRepository()
    
    # ── Connect To Database ───────────────────────
    await _db_instance.connect()
    
    return _db_instance

async def close_database() -> None:
    """Close the active database connection"""
    global _db_instance
    
    if _db_instance:
        await _db_instance.disconnect()
        _db_instance = None

def get_database() -> DatabaseRepository:
    """
    Get the active database instance
    Use this in your API routes!
    """
    if _db_instance is None:
        raise RuntimeError(
            "Database not initialized! "
            "Call init_database() first."
        )
    return _db_instance

