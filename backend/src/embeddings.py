from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import torch
import warnings
import logging
import os

load_dotenv()

# ── Suppress Warnings ─────────────────────────────
warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_embeddings():
    """
    Load sentence-transformers embedding model
    Automatically uses GPU if available!
    """
    embedding_model = os.getenv(
        "EMBEDDING_MODEL", 
        "all-MiniLM-L6-v2"
    )
    
    # ── Auto detect GPU or CPU ────────────────────
    if torch.cuda.is_available():
        device = "cuda"
        print(f"🚀 GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("💻 No GPU found, using CPU")
    
    print(f"Loading embedding model: {embedding_model}")
    print(f"Using device: {device}")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": device},  # ← Auto GPU/CPU
        encode_kwargs={"normalize_embeddings": True}
    )
    
    print("✅ Embedding model loaded successfully!")
    return embeddings