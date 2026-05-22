# api/routes.py
from database.metrics_crud import log_metric
from database.metrics_models import MetricLog
from auth.dependencies import get_current_user

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.schemas import (
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    HealthResponse
)
import time
import uuid
from src.graph import rag_graph
from src.data_loader import ingest_documents
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from src.prompts import (
    BEGINNER_PROMPT,
    EXPERT_PROMPT,
    TOPIC_GUARD_PROMPT,
    CLASSIFY_PROMPT
)
from src.vectorstore import get_retriever
from src.nodes import format_chat_history
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ── Initialize Router ─────────────────────────────
router = APIRouter()

# ── Initialize LLM For Streaming ──────────────────
streaming_llm = ChatOllama(
    base_url   = os.getenv("OLLAMA_BASE_URL",
                           "http://127.0.0.1:11434"),
    model      = os.getenv("OLLAMA_MODEL",
                           "llama3.1:8b"),
    temperature= 0.7,
    streaming  = True
)

# ── Initialize Retriever ──────────────────────────
# ── Lazy Retriever Initialization ─────────────────
_retriever = None

def _get_retriever():
    """Lazy load retriever after vector DB initialized"""
    global _retriever
    if _retriever is None:
        _retriever = get_retriever()
    return _retriever


parser     = StrOutputParser()

# ─────────────────────────────────────────────────
# ROUTE 1 - Health Check
# ─────────────────────────────────────────────────
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    return HealthResponse(
        status  = "ok",
        message = "Interior Design RAG API is running!"
    )

# ─────────────────────────────────────────────────
# ROUTE 2 - Chat (Non-streaming backup)
# ─────────────────────────────────────────────────
@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"]
)
async def chat(request: ChatRequest):
    try:
        print(f"\n{'='*50}")
        print(f"Question: {request.question}")
        print(f"{'='*50}\n")

        # Convert history to dict format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.chat_history or [])
        ]

        result = rag_graph.invoke({
            "question"          : request.question,
            "chat_history"      : history,
            "user_level"        : None,
            "documents"         : None,
            "generation"        : None,
            "is_relevant"       : None,
            "retry_count"       : 0,
            "is_design_related" : None
        })

        answer     = result.get("generation", "")
        user_level = result.get("user_level", "BEGINNER")

        is_relevant  = result.get("is_relevant", True)
        is_off_topic = (
            is_relevant == False and
            answer != "" and
            result.get("documents") is None
        )

        if not answer:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate answer"
            )

        return ChatResponse(
            question   = request.question,
            answer     = answer,
            user_level = "OFF_TOPIC" if is_off_topic else user_level,
            success    = True
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────────
# ROUTE 3 - Chat Stream (With Memory!)
# ─────────────────────────────────────────────────
@router.post(
    "/chat/stream",
    tags=["Chat"]
)
async def chat_stream(request: ChatRequest, user: dict = Depends(get_current_user)):
    """
    Streaming chat endpoint with memory!
    """

    print(f"\n🔵 CHAT_STREAM ENDPOINT HIT! User: {user.get('uid', 'unknown')}")

    async def generate():
        # ── Metric Tracking Variables ─────────────
        start_time       = time.time()
        metric_user_level= "BEGINNER"
        metric_off_topic = False
        metric_retrieved = 0
        metric_retries   = 0
        full_answer      = ""
        retrieved_texts  = []

        try:
            print(f"\n{'='*50}")
            print(f"Streaming Question: {request.question}")
            print(f"History Length: {len(request.chat_history or [])}")
            print(f"{'='*50}\n")

            # ── Convert history to dict ───────────
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in (request.chat_history or [])
            ]

            formatted_history = format_chat_history(history)

            # ── Step 1: Check Topic ───────────────
            topic_chain  = TOPIC_GUARD_PROMPT | streaming_llm | parser
            topic_result = topic_chain.invoke({
                "question": request.question
            })

            is_design = "YES" in topic_result.strip().upper()

            if not is_design:
                metric_off_topic = True

                rejection = """I'm specialized in interior design only! 🏠

I cannot help with that topic. But I'd love to help you with:

- 🛋️ **Room decoration ideas**
- 🎨 **Color schemes and palettes**
- 💡 **Lighting design tips**
- 🪑 **Furniture arrangement**
- 🏛️ **Design styles and history**
- 📐 **Space planning**

What would you like to know about interior design?"""

                full_answer = rejection

                yield f"data: {json.dumps({'type': 'metadata', 'user_level': 'OFF_TOPIC'})}\n\n"

                for word in rejection.split(" "):
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

                # ── Log Off-Topic Metric ──────────
                latency = (time.time() - start_time) * 1000
                metric = MetricLog(
                    id              = str(uuid.uuid4()),
                    user_id         = user["uid"],
                    question        = request.question,
                    answer          = full_answer,
                    latency_ms      = round(latency, 2),
                    token_estimate  = len(full_answer.split()),
                    user_level      = "OFF_TOPIC",
                    is_off_topic    = True,
                    retrieved_count = 0,
                    retry_count     = 0,
                    retrieved_contexts = []
                )
                await log_metric(metric)

                # Send metric_id so frontend can rate
                yield f"data: {json.dumps({'type': 'metric', 'metric_id': metric.id})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            # ── Step 2: Classify User ─────────────
            classify_chain  = CLASSIFY_PROMPT | streaming_llm | parser
            classify_result = classify_chain.invoke({
                "question": request.question
            })

            user_level = "EXPERT" if "EXPERT" in \
                classify_result.strip().upper() \
                else "BEGINNER"
            metric_user_level = user_level

            print(f"--- User Level: {user_level} ---")

            # ── Step 3: Retrieve Documents ────────
            documents = _get_retriever().invoke(request.question)
            metric_retrieved = len(documents)
            retrieved_texts  = [doc.page_content for doc in documents]
            print(f"--- Retrieved {len(documents)} docs ---")

            # ── Step 4: Build Context ─────────────
            context = "\n\n".join([
                doc.page_content for doc in documents
            ])

            # ── Step 5: Choose Prompt ─────────────
            prompt = EXPERT_PROMPT \
                if user_level == "EXPERT" \
                else BEGINNER_PROMPT

            # ── Step 6: Send Metadata ─────────────
            yield f"data: {json.dumps({'type': 'metadata', 'user_level': user_level})}\n\n"

            # ── Step 7: Stream Answer ─────────────
            print("--- Streaming Answer With Memory ---")
            stream_chain = prompt | streaming_llm

            async for chunk in stream_chain.astream({
                "question"    : request.question,
                "context"     : context,
                "chat_history": formatted_history
            }):
                if chunk.content:
                    full_answer += chunk.content
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

            # ── Step 8: Log Metric ────────────────
            latency = (time.time() - start_time) * 1000
            metric = MetricLog(
                id                = str(uuid.uuid4()),
                user_id           = user["uid"],
                question          = request.question,
                answer            = full_answer,
                latency_ms        = round(latency, 2),
                token_estimate    = len(full_answer.split()),
                user_level        = metric_user_level,
                is_off_topic      = False,
                retrieved_count   = metric_retrieved,
                retry_count       = metric_retries,
                retrieved_contexts= retrieved_texts
            )
            await log_metric(metric)
            print(f"--- Metric logged: {metric.id} ---")

            # Send metric_id to frontend
            yield f"data: {json.dumps({'type': 'metric', 'metric_id': metric.id})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            print("--- Stream Complete ---")

        except Exception as e:
            import traceback
            print(f"\n{'!'*50}")
            print(f"STREAM ERROR: {str(e)}")
            print(f"ERROR TYPE: {type(e).__name__}")
            print("FULL TRACEBACK:")
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





# ─────────────────────────────────────────────────
# ROUTE 4 - Ingest Documents
# ─────────────────────────────────────────────────
@router.post(
    "/ingest",
    response_model=IngestResponse,
    tags=["Documents"]
)
async def ingest(request: IngestRequest):
    try:
        if not request.confirm:
            return IngestResponse(
                success = False,
                message = "Ingestion cancelled!"
            )

        print("\nStarting document ingestion...")
        ingest_documents()

        return IngestResponse(
            success = True,
            message = "Documents ingested successfully!"
        )

    except Exception as e:
        print(f"Ingestion Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )