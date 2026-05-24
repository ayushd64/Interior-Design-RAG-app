# api/agent_routes.py
"""
Agentic chat endpoint.
The agent decides which tools to use (search, image)
and streams the response back.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.schemas import ChatRequest
from auth.dependencies import get_current_user
from src.agent import get_agent
from langchain_core.messages import HumanMessage, AIMessage
import json

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/stream")
async def agent_stream(
    request: ChatRequest,
    user   : dict = Depends(get_current_user)
):
    """
    Agentic streaming endpoint.
    Agent autonomously decides to search, generate
    images, or just chat.
    """
    print(f"\n🤖 AGENT ENDPOINT HIT! User: {user.get('uid')}")

    async def generate():
        try:
            print(f"\n{'='*50}")
            print(f"Agent Question: {request.question}")
            print(f"{'='*50}\n")

            agent = get_agent()

            # ── Build message history ─────────────
            messages = []
            for msg in (request.chat_history or []):
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                else:
                    messages.append(AIMessage(content=msg.content))
            
            # Add current question
            messages.append(HumanMessage(content=request.question))

            # ── Run the agent ─────────────────────
            # The agent will think → use tools → respond
            print("--- Agent thinking... ---")
            
            result = agent.invoke({"messages": messages})

            # ── Extract the final answer ──────────
            final_message = result["messages"][-1]
            answer = final_message.content

            # ── Detect if any image was generated ─
            # Look through tool results for IMAGE_GENERATED
            image_url = None
            for msg in result["messages"]:
                if type(msg).__name__ == "ToolMessage":
                    if "IMAGE_GENERATED::" in str(msg.content):
                        image_url = str(msg.content).split(
                            "IMAGE_GENERATED::"
                        )[1].strip()
                        print(f"--- Image detected: {image_url[:60]}... ---")

            # ── Send metadata ─────────────────────
            yield f"data: {json.dumps({'type': 'metadata', 'user_level': 'AGENT'})}\n\n"

            # ── If image, send it first ───────────
            if image_url:
                yield f"data: {json.dumps({'type': 'image', 'url': image_url})}\n\n"

            # ── Stream the text answer word by word ─
            print("--- Streaming agent answer ---")
            for word in answer.split(" "):
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            print("--- Agent response complete ---")

        except Exception as e:
            import traceback
            print(f"\n{'!'*50}")
            print(f"AGENT ERROR: {str(e)}")
            traceback.print_exc()
            print(f"{'!'*50}\n")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control"              : "no-cache",
            "Connection"                 : "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

