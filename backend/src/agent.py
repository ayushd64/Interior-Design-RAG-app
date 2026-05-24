# src/agent.py
"""
The AGENTIC brain of our RAG system.
Uses LangGraph's prebuilt ReAct agent to let
llama3.1 decide which tools to use.
"""
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from src.agent_tools import get_agent_tools
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# The System Prompt — the agent's "personality"
# and INSTRUCTIONS on how to behave
# ─────────────────────────────────────────────────
# This is where we fix the "robotic Test 3" problem!
# We tell the agent EXACTLY how to act.

AGENT_SYSTEM_PROMPT = """You are a friendly, expert \
interior design assistant.

You have access to these tools:
1. search_interior_design_knowledge - for factual \
questions about design styles, history, techniques, \
color theory, furniture, lighting, space planning.
2. generate_interior_image - when the user wants to \
SEE, VISUALIZE, or be SHOWN a room or design.

GUIDELINES:
- For design QUESTIONS, use search_interior_design_knowledge \
to find accurate information, then answer warmly.
- When the user wants to SEE something (words like "show me", \
"visualize", "what does X look like", "generate", "picture"), \
use generate_interior_image with a rich, detailed description.
- For greetings or casual chat, just respond warmly WITHOUT \
using any tools. No need to mention tools or functions.
- You can use BOTH tools if needed (e.g. explain a style \
AND show an image of it).
- Stay focused on interior design. Politely decline \
unrelated topics.
- Be warm, helpful, and concise.

Never mention "functions" or "tools" to the user. \
Just help them naturally."""

# ─────────────────────────────────────────────────
# Build the agent (lazy - so it loads after startup)
# ─────────────────────────────────────────────────
_agent = None

def get_agent():
    """Lazy-load the agent (built once, reused)"""
    global _agent
    if _agent is None:
        print("🤖 Building agent...")
        
        # The LLM that powers the agent
        llm = ChatOllama(
            base_url    = os.getenv(
                "OLLAMA_BASE_URL",
                "http://127.0.0.1:11434"
            ),
            model       = os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature = 0.3   # slight creativity for natural replies
        )
        
        # Get our tools
        tools = get_agent_tools()
        
        # create_react_agent builds the ENTIRE
        # think→act→observe loop for us!
        _agent = create_react_agent(
            model        = llm,
            tools        = tools,
            prompt       = AGENT_SYSTEM_PROMPT
        )
        
        print("✅ Agent built successfully!")
    
    return _agent

