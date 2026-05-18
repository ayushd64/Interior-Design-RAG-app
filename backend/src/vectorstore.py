from langchain_chroma import Chroma
from src.embeddings import get_embeddings
from dotenv import load_dotenv
import os

load_dotenv()

def get_vectorstore():
    """
    Connect to ChromaDB vectorstore
    """
    embeddings = get_embeddings()
    
    chroma_path = os.getenv(
        "CHROMA_DB_PATH", 
        "./vectorstore/chromadb"
    )
    collection_name = os.getenv(
        "CHROMA_COLLECTION_NAME", 
        "interior_design"
    )
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=chroma_path
    )
    
    print("✅ ChromaDB connected successfully!")
    return vectorstore

def get_retriever():
    """
    Get retriever from vectorstore
    Returns top 4 most relevant documents
    """
    vectorstore = get_vectorstore()
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    print("✅ Retriever ready!")
    return retriever