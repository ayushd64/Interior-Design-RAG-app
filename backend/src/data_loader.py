# src/data_loader.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.vector_db.factory import get_vector_db, init_vector_db
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

def load_documents():
    """Load all PDFs from data/raw folder"""
    data_path = "./data/raw"
    
    print(f"Loading documents from {data_path}...")
    
    loader = DirectoryLoader(
        data_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages!")
    return documents

def split_documents(documents):
    """Split documents into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size      = 1000,
        chunk_overlap   = 200,
        length_function = len
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks!")
    return chunks

async def ingest_documents_async():
    """
    Full pipeline (async version):
    Load → Split → Embed → Store in active Vector DB
    """
    print("Starting document ingestion...")
    
    # ── Initialize vector DB ──────────────────────
    vector_db = await init_vector_db()
    
    # ── Load documents ────────────────────────────
    documents = load_documents()
    
    if not documents:
        print("❌ No documents found in data/raw folder!")
        print("Please add PDF files to backend/data/raw/")
        return
    
    # ── Split into chunks ─────────────────────────
    chunks = split_documents(documents)
    
    # ── Store in vector DB ────────────────────────
    vector_db.add_documents(chunks)
    
    print(f"✅ Successfully ingested {len(chunks)} chunks!")
    print("✅ Documents are ready for RAG!")

def ingest_documents():
    """
    Sync wrapper for ingestion
    Used by API endpoints and CLI
    """
    asyncio.run(ingest_documents_async())

if __name__ == "__main__":
    ingest_documents()

