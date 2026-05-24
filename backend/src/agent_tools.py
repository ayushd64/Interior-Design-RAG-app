# src/agent_tools.py
"""
TOOLS for the agentic RAG system.
Each @tool function is something the agent can
CHOOSE to call based on the user's request.
"""
from langchain_core.tools import tool
from src.vectorstore import get_retriever
from urllib.parse import quote
import os

# ─────────────────────────────────────────────────
# TOOL 1: Search Knowledge Base (your existing RAG!)
# ─────────────────────────────────────────────────
@tool
def search_interior_design_knowledge(query: str) -> str:
    """Search the interior design knowledge base for 
    information about design styles, history, techniques, 
    color theory, furniture, lighting, and space planning.
    
    Use this for ANY factual question about interior design.
    
    Args:
        query: The search query about interior design
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant information found."
        
        # Combine the retrieved chunks
        context = "\n\n".join([
            doc.page_content for doc in docs
        ])
        return context
    except Exception as e:
        return f"Error searching knowledge: {str(e)}"

# ─────────────────────────────────────────────────
# TOOL 2: Generate Image (Pollinations)
# ─────────────────────────────────────────────────
@tool
def generate_interior_image(description: str) -> str:
    """Generate a visual image/render of an interior 
    design based on a description. 
    
    Use this when the user wants to SEE, VISUALIZE, or 
    asks to be SHOWN an interior design, room, or space.
    
    Args:
        description: Detailed description of the interior 
                     to visualize (room type, style, colors, 
                     lighting, furniture, mood)
    """
    import re
    
    # ── Clean the description ─────────────────────
    # Remove parentheses, brand names in parens, etc.
    clean = re.sub(r'\([^)]*\)', '', description)  # remove (...)
    clean = clean.replace('"', '').replace("'", '')
    clean = ' '.join(clean.split())  # normalize whitespace
    
    # ── Limit length (URLs have limits!) ──────────
    # Keep first ~200 chars to avoid overly long URLs
    if len(clean) > 200:
        clean = clean[:200]
    
    # ── Add quality keywords ──────────────────────
    enhanced = (
        f"{clean}, interior design, professional "
        f"photography, high quality, well-lit"
    )
    
    # URL-encode
    encoded = quote(enhanced)
    
    # Build URL with landscape dimensions
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1280&height=720&nologo=true"
    )
    
    print(f"--- Image URL length: {len(url)} chars ---")
    
    return f"IMAGE_GENERATED::{url}"



# ─────────────────────────────────────────────────
# Export all tools as a list
# ─────────────────────────────────────────────────
def get_agent_tools():
    """Return all available tools for the agent"""
    return [
        search_interior_design_knowledge,
        generate_interior_image
    ]

