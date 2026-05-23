# database/metrics_crud.py
from typing import List, Optional
from database.factory import get_database
from database.metrics_models import MetricLog

async def log_metric(metric: MetricLog) -> None:
    db = get_database()
    await db.log_metric(metric)

async def get_metrics(
    user_id: str,
    limit  : int = 100
) -> List[MetricLog]:
    db = get_database()
    return await db.get_metrics(user_id, limit)

async def get_metric(
    metric_id: str,
    user_id  : str
) -> Optional[MetricLog]:
    db = get_database()
    return await db.get_metric(metric_id, user_id)

async def update_metric_rating(
    metric_id: str,
    user_id  : str,
    rating   : int
) -> bool:
    db = get_database()
    return await db.update_metric_rating(
        metric_id, user_id, rating
    )


async def update_metric_scores(
    metric_id: str,
    scores   : dict
) -> bool:
    db = get_database()
    return await db.update_metric_scores(metric_id, scores)

