# test_agent.py
"""Test the agent end-to-end before building the endpoint"""
from src.agent import get_agent
from langchain_core.messages import HumanMessage

def test(question: str):
    print(f"\n{'='*55}")
    print(f"USER: {question}")
    print(f"{'='*55}")
    
    agent = get_agent()
    
    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })
    
    # Show ALL messages to see what tools were called
    print("\n--- FULL CONVERSATION TRACE ---")
    for msg in result["messages"]:
        msg_type = type(msg).__name__
        
        # Tool calls (agent deciding to use a tool)
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"🔧 TOOL CALL: {tc['name']}")
                print(f"   Args: {tc['args']}")
        
        # Tool results
        elif msg_type == "ToolMessage":
            print(f"📥 TOOL RESULT: {msg.content[:150]}")
        
        # Agent/AI text
        elif msg_type == "AIMessage" and msg.content:
            print(f"🤖 AGENT TEXT: {msg.content[:200]}")
        
        # User
        elif msg_type == "HumanMessage":
            print(f"👤 USER: {msg.content}")
    
    print("--- END TRACE ---")


# ─── THIS BLOCK MUST BE AT THE BOTTOM! ─── 
if __name__ == "__main__": 
    print("\n🤖 TESTING THE AGENT\n") 
    
    test("What is Art Deco style?") 
    test("Show me a minimalist bedroom") 
    test("Hi there!") 
    
    print(f"\n{'='*55}") 
    print("🏁 DONE!") 
    print(f"{'='*55}\n") 

