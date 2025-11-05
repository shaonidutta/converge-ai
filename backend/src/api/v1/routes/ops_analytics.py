"""
Operations Analytics API Routes

Provides comprehensive analytics endpoints for operations dashboard:
- KPI metrics (bookings, revenue, complaints, resolution time, satisfaction, utilization)
- Trend data (daily/weekly/monthly trends)
- Category distribution
- Status distribution
- Performance metrics
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_staff
from src.core.models.staff import Staff
from src.services.ops_analytics_service import OpsAnalyticsService
from src.schemas.ops_analytics import (
    AnalyticsKPIResponse,
    AnalyticsTrendResponse,
    AnalyticsCategoryResponse,
    AnalyticsStatusResponse,
    AnalyticsPerformanceResponse,
    TimeRange
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Operations Analytics"])


@router.get("/kpis", response_model=AnalyticsKPIResponse)
async def get_analytics_kpis(
    time_range: TimeRange = Query(TimeRange.WEEK, description="Time range for analytics"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff)
):
    """
    Get Key Performance Indicators (KPIs) for analytics dashboard
    
    Returns:
    - Total Bookings with percentage change
    - Total Revenue with percentage change
    - Active Complaints with percentage change
    - Average Resolution Time with percentage change
    - Customer Satisfaction score with percentage change
    - Staff Utilization percentage with percentage change
    """
    service = OpsAnalyticsService(db)
    return await service.get_kpis(time_range, start_date, end_date)


@router.get("/trends", response_model=AnalyticsTrendResponse)
async def get_analytics_trends(
    time_range: TimeRange = Query(TimeRange.WEEK, description="Time range for trends"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff)
):
    """
    Get trend data for bookings, revenue, and complaints over time
    
    Returns daily/weekly/monthly data points based on time range
    """
    service = OpsAnalyticsService(db)
    return await service.get_trends(time_range, start_date, end_date)


@router.get("/categories", response_model=AnalyticsCategoryResponse)
async def get_category_distribution(
    time_range: TimeRange = Query(TimeRange.WEEK, description="Time range for category data"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff)
):
    """
    Get service category distribution
    
    Returns breakdown of bookings by service category with percentages
    """
    service = OpsAnalyticsService(db)
    return await service.get_category_distribution(time_range, start_date, end_date)


@router.get("/status", response_model=AnalyticsStatusResponse)
async def get_status_distribution(
    time_range: TimeRange = Query(TimeRange.WEEK, description="Time range for status data"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff)
):
    """
    Get booking status distribution
    
    Returns breakdown of bookings by status (Completed, In Progress, Pending, Cancelled)
    """
    service = OpsAnalyticsService(db)
    return await service.get_status_distribution(time_range, start_date, end_date)


@router.get("/performance", response_model=AnalyticsPerformanceResponse)
async def get_performance_metrics(
    time_range: TimeRange = Query(TimeRange.WEEK, description="Time range for performance data"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff)
):
    """
    Get performance metrics vs targets
    
    Returns current performance and target values for:
    - Response Time
    - Resolution Rate
    - Customer Satisfaction
    - Staff Efficiency
    - SLA Compliance
    """
    service = OpsAnalyticsService(db)
    return await service.get_performance_metrics(time_range, start_date, end_date)

