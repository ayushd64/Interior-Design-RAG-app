import chromadb
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def inspect_chromadb():
    """
    Inspect ChromaDB data
    """
    chroma_path = os.getenv(
        "CHROMA_DB_PATH",
        "./vectorstore/chromadb"
    )
    collection_name = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "interior_design"
    )

    print("\n" + "="*60)
    print("🔍 ChromaDB Inspector")
    print("="*60)

    # ── Connect to ChromaDB ───────────────────────
    client     = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection(collection_name)
    count      = collection.count()

    print(f"\n📚 Collection : {collection_name}")
    print(f"📊 Total Chunks: {count}")

    # ── Preview First 5 Chunks ────────────────────
    print(f"\n👀 First 5 Chunks:")
    print("-"*60)

    results = collection.peek(limit=5)

    for i, (doc_id, document, metadata) in enumerate(zip(
        results['ids'],
        results['documents'],
        results['metadatas']
    )):
        print(f"\n📄 Chunk {i+1}:")
        print(f"   ID      : {doc_id[:20]}...")
        print(f"   Source  : {metadata.get('source', 'Unknown')}")
        print(f"   Page    : {metadata.get('page', 'Unknown')}")
        print(f"   Preview : {document[:150]}...")
        print("-"*60)

def inspect_sqlite():
    """
    Inspect SQLite3 tables directly
    """
    db_path = os.getenv(
        "CHROMA_DB_PATH",
        "./vectorstore/chromadb"
    )
    sqlite_path = f"{db_path}/chroma.sqlite3"

    print("\n" + "="*60)
    print("🗄️  SQLite3 Inspector")
    print("="*60)

    conn   = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # ── Show All Tables With Row Counts ──────────
    print("\n📊 All Tables:")
    print("-"*60)

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            )
            count = cursor.fetchone()[0]
            print(f"   {table_name:<40} → {count} rows")
        except:
            print(f"   {table_name:<40} → (system table)")

    # ── Show Collections ──────────────────────────
    print(f"\n📚 Collections Table:")
    print("-"*60)

    cursor.execute("""
        SELECT id, name, dimension
        FROM collections
    """)
    collections = cursor.fetchall()

    for col in collections:
        print(f"   ID        : {col[0]}")
        print(f"   Name      : {col[1]}")
        print(f"   Dimension : {col[2]}")

    # ── Show Sample Metadata ──────────────────────
    print(f"\n🏷️  Sample Metadata (First 10):")
    print("-"*60)

    cursor.execute("""
        SELECT 
            em.id,
            em.key,
            em.string_value,
            em.int_value
        FROM embedding_metadata em
        LIMIT 10
    """)
    metadata = cursor.fetchall()

    for row in metadata:
        print(f"   ID    : {row[0]}")
        print(f"   Key   : {row[1]}")
        print(f"   Value : {row[2] or row[3]}")
        print()

    # ── Show Embedding Count ──────────────────────
    print(f"\n🧮 Embeddings Table:")
    print("-"*60)

    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total = cursor.fetchone()[0]
    print(f"   Total Embeddings: {total}")

    cursor.execute("""
        SELECT id, seq_id
        FROM embeddings
        LIMIT 3
    """)
    sample = cursor.fetchall()

    print(f"\n   Sample Rows:")
    for row in sample:
        print(f"   → ID: {row[0]}, Seq: {row[1]}")

    conn.close()

    print("\n" + "="*60)
    print("✅ Inspection Complete!")
    print("="*60 + "\n")

def search_similar(query: str, n_results: int = 3):
    """
    Search for similar chunks
    """
    from src.embeddings import get_embeddings
    from langchain_chroma import Chroma

    chroma_path = os.getenv(
        "CHROMA_DB_PATH",
        "./vectorstore/chromadb"
    )
    collection_name = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "interior_design"
    )

    print(f"\n{'='*60}")
    print(f"🔍 Searching: '{query}'")
    print("="*60)

    embeddings  = get_embeddings()
    vectorstore = Chroma(
        collection_name  = collection_name,
        embedding_function = embeddings,
        persist_directory= chroma_path
    )

    results = vectorstore.similarity_search_with_score(
        query,
        k=n_results
    )

    for i, (doc, score) in enumerate(results):
        relevance = (1 - score) * 100
        print(f"\n🎯 Result {i+1}:")
        print(f"   Relevance : {relevance:.1f}%")
        print(f"   Source    : {doc.metadata.get('source', 'Unknown')}")
        print(f"   Page      : {doc.metadata.get('page', 'Unknown')}")
        print(f"   Content   : {doc.page_content[:200]}...")
        print("-"*60)

if __name__ == "__main__":
    
    print("\nWhat do you want to inspect?")
    print("1 → ChromaDB Overview")
    print("2 → SQLite3 Tables")
    print("3 → Search Similar Chunks")
    print("4 → All of the above")

    choice = input("\nEnter choice (1/2/3/4): ")

    if choice == "1":
        inspect_chromadb()
    elif choice == "2":
        inspect_sqlite()
    elif choice == "3":
        query = input("Enter search query: ")
        search_similar(query)
    elif choice == "4":
        inspect_chromadb()
        inspect_sqlite()
        query = input("\nEnter search query: ")
        search_similar(query)
    else:
        print("Invalid choice!")