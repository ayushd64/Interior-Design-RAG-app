# test_tool_calling.py
"""
PROOF OF CONCEPT: Can llama3.1:8b call tools?
This is a throwaway test script to verify
tool-calling works before we build the full agent.
"""
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# STEP 1: Define a simple test tool
# ─────────────────────────────────────────────────
# The @tool decorator turns a function into something
# the LLM can "see" and decide to call.
# The docstring is CRITICAL - the LLM reads it to
# understand what the tool does!

@tool
def get_room_dimensions(room_type: str) -> str:
    """Get typical dimensions for a room type.
    
    Args:
        room_type: The type of room (e.g. bedroom, kitchen)
    """
    # Fake data - just for testing!
    dimensions = {
        "bedroom" : "12x14 feet (typical)",
        "kitchen" : "10x12 feet (typical)",
        "bathroom": "5x8 feet (typical)"
    }
    return dimensions.get(
        room_type.lower(),
        "Unknown room type"
    )

@tool
def generate_image(description: str) -> str:
    """Generate an image from a text description.
    
    Args:
        description: What the image should show
    """
    # Fake - just returns confirmation for the test
    return f"[Image generated for: {description}]"

# ─────────────────────────────────────────────────
# STEP 2: Set up the LLM WITH tools bound to it
# ─────────────────────────────────────────────────
llm = ChatOllama(
    base_url    = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    model       = os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    temperature = 0.0
)

# This is the KEY line - we "bind" tools to the LLM
# Now the LLM KNOWS about these tools and CAN call them
tools = [get_room_dimensions, generate_image]
llm_with_tools = llm.bind_tools(tools)

# ─────────────────────────────────────────────────
# STEP 3: Test with different prompts
# ─────────────────────────────────────────────────
def test_prompt(prompt: str):
    print(f"\n{'='*55}")
    print(f"USER: {prompt}")
    print(f"{'='*55}")
    
    response = llm_with_tools.invoke(prompt)
    
    # Did the LLM decide to call a tool?
    if response.tool_calls:
        print("✅ LLM CHOSE TO USE TOOL(S):")
        for tc in response.tool_calls:
            print(f"   🔧 Tool: {tc['name']}")
            print(f"      Args: {tc['args']}")
    else:
        print("💬 LLM responded with TEXT (no tool):")
        print(f"   {response.content[:200]}")

# ─────────────────────────────────────────────────
# RUN THE TESTS
# ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🧪 TESTING llama3.1:8b TOOL-CALLING\n")
    
    # Test 1: Should call get_room_dimensions
    test_prompt("What are the typical dimensions of a bedroom?")
    
    # Test 2: Should call generate_image
    test_prompt("Show me a picture of a cozy living room")
    
    # Test 3: Should NOT call any tool (just chat)
    test_prompt("Hello, how are you?")
    
    # Test 4: Might call generate_image
    test_prompt("I want to see what a modern kitchen looks like")
    
    print(f"\n{'='*55}")
    print("🏁 TEST COMPLETE!")
    print(f"{'='*55}\n")

