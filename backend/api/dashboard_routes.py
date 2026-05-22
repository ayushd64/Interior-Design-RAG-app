# api/dashboard_routes.py
from fastapi import APIRouter, HTTPException, Depends
from database.metrics_crud import (
    get_metrics,
    update_metric_rating
)
from database.metrics_models import (
    DashboardStats,
    RatingRequest,
    MetricLog
)
from auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ── Get Dashboard Stats ───────────────────────────
@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: dict = Depends(get_current_user)
):
    """Aggregate stats for the dashboard"""
    metrics = await get_metrics(user["uid"], limit=1000)

    total = len(metrics)

    if total == 0:
        return DashboardStats(
            total_queries       = 0,
            off_topic_count     = 0,
            off_topic_rate      = 0.0,
            avg_latency_ms      = 0.0,
            avg_retrieved_count = 0.0,
            total_retries       = 0,
            beginner_count      = 0,
            expert_count        = 0,
            positive_ratings    = 0,
            negative_ratings    = 0
        )

    off_topic   = sum(1 for m in metrics if m.is_off_topic)
    beginner    = sum(1 for m in metrics if m.user_level == "BEGINNER")
    expert      = sum(1 for m in metrics if m.user_level == "EXPERT")
    pos_ratings = sum(1 for m in metrics if m.user_rating == 1)
    neg_ratings = sum(1 for m in metrics if m.user_rating == -1)
    total_retry = sum(m.retry_count for m in metrics)

    # Averages (exclude off-topic for retrieval/latency relevance)
    on_topic = [m for m in metrics if not m.is_off_topic]
    avg_latency   = (
        sum(m.latency_ms for m in metrics) / total
    )
    avg_retrieved = (
        sum(m.retrieved_count for m in on_topic) / len(on_topic)
        if on_topic else 0.0
    )

    # RAGAS averages (Phase 2 - only if available)
    faith_scores = [
        m.faithfulness for m in metrics 
        if m.faithfulness is not None
    ]
    rel_scores = [
        m.answer_relevancy for m in metrics 
        if m.answer_relevancy is not None
    ]

    return DashboardStats(
        total_queries       = total,
        off_topic_count     = off_topic,
        off_topic_rate      = round(off_topic / total * 100, 1),
        avg_latency_ms      = round(avg_latency, 1),
        avg_retrieved_count = round(avg_retrieved, 1),
        total_retries       = total_retry,
        beginner_count      = beginner,
        expert_count        = expert,
        positive_ratings    = pos_ratings,
        negative_ratings    = neg_ratings,
        avg_faithfulness    = (
            round(sum(faith_scores) / len(faith_scores), 2)
            if faith_scores else None
        ),
        avg_answer_relevancy= (
            round(sum(rel_scores) / len(rel_scores), 2)
            if rel_scores else None
        )
    )

# ── Get Recent Metrics (for table) ────────────────
@router.get("/metrics", response_model=List[MetricLog])
async def get_recent_metrics(
    limit: int = 50,
    user : dict = Depends(get_current_user)
):
    """Get recent metric logs"""
    return await get_metrics(user["uid"], limit=limit)

# ── Rate A Query ──────────────────────────────────
@router.post("/rate")
async def rate_query(
    request: RatingRequest,
    user   : dict = Depends(get_current_user)
):
    """Submit thumbs up/down rating"""
    success = await update_metric_rating(
        request.metric_id,
        user["uid"],
        request.rating
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Metric not found"
        )
    return {"success": True}

