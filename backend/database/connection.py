# database/connection.py
from database.factory import init_database, close_database

# ─────────────────────────────────────────────────
# Wrappers that use the factory
# Kept for backwards compatibility
# ─────────────────────────────────────────────────

async def connect_to_mongo():
    """
    Initialize database based on DATABASE_TYPE env
    Despite the name, this works with any database!
    """
    await init_database()

async def close_mongo_connection():
    """Close active database connection"""
    await close_database()

