# database/metrics_models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ─────────────────────────────────────────────────
# Metric Log Entry
# ─────────────────────────────────────────────────
class MetricLog(BaseModel):
    """
    Single metric entry logged per query
    """
    id              : str
    user_id         : str
    question        : str
    answer          : str
    
    # ── Performance Metrics ───────────────────────
    latency_ms      : float                    # Response time
    token_estimate  : int                      # Approx tokens
    
    # ── RAG Metrics ───────────────────────────────
    user_level      : str                      # BEGINNER/EXPERT
    is_off_topic    : bool                      # Topic guard result
    retrieved_count : int                       # Docs retrieved
    retry_count     : int                       # Rephrasing retries
    docs_relevant   : Optional[bool] = None     # Grading result
    answer_grounded : Optional[bool] = None     # Hallucination check
    
    # ── RAGAS Scores (Phase 2 - filled later) ────
    faithfulness    : Optional[float] = None
    answer_relevancy: Optional[float] = None
    context_precision: Optional[float] = None
    
    # ── User Feedback ─────────────────────────────
    user_rating     : Optional[int] = None      # 1=👍, -1=👎, None=no rating
    
    # ── Context (for RAGAS later) ─────────────────
    retrieved_contexts: Optional[List[str]] = None
    
    timestamp       : datetime = Field(
        default_factory=datetime.utcnow
    )

# ─────────────────────────────────────────────────
# Dashboard Summary Stats
# ─────────────────────────────────────────────────
class DashboardStats(BaseModel):
    """
    Aggregated stats for dashboard
    """
    total_queries       : int
    off_topic_count     : int
    off_topic_rate      : float
    avg_latency_ms      : float
    avg_retrieved_count : float
    total_retries       : int
    beginner_count      : int
    expert_count        : int
    positive_ratings    : int
    negative_ratings    : int
    
    # ── RAGAS Averages (if available) ─────────────
    avg_faithfulness    : Optional[float] = None
    avg_answer_relevancy: Optional[float] = None
    avg_context_precision: Optional[float] = None

# ─────────────────────────────────────────────────
# Rating Request
# ─────────────────────────────────────────────────
class RatingRequest(BaseModel):
    """Request to rate a query"""
    metric_id: str
    rating   : int          # 1 or -1

