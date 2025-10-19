"""
Metrics endpoint for Prometheus scraping

Exposes /metrics endpoint in Prometheus text format
"""
import logging
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.monitoring.metrics.prometheus_metrics import get_metrics_registry

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    
    Returns metrics in Prometheus text format for scraping.
    
    This endpoint should be scraped by Prometheus server at regular intervals.
    
    Example Prometheus config:
    ```yaml
    scrape_configs:
      - job_name: 'convergeai'
        scrape_interval: 15s
        static_configs:
          - targets: ['localhost:8000']
    ```
    
    Returns:
        Metrics in Prometheus text format
    """
    registry = get_metrics_registry()
    metrics_output = generate_latest(registry)
    
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )

