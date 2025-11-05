"""
Operations Analytics Service

Business logic for analytics data aggregation and calculations
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models.booking import Booking
from src.core.models.complaint import Complaint
from src.core.models.category import Category
from src.schemas.ops_analytics import (
    AnalyticsKPIResponse,
    AnalyticsTrendResponse,
    AnalyticsCategoryResponse,
    AnalyticsStatusResponse,
    AnalyticsPerformanceResponse,
    KPIMetric,
    TrendDataPoint,
    CategoryData,
    StatusData,
    PerformanceMetric,
    TimeRange
)

logger = logging.getLogger(__name__)


class OpsAnalyticsService:
    """Service for operations analytics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _get_date_range(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Tuple[datetime, datetime]:
        """
        Calculate date range based on time_range parameter
        
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        now = datetime.now()
        
        if time_range == TimeRange.CUSTOM and start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return start, end
        
        if time_range == TimeRange.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_range == TimeRange.WEEK:
            start = now - timedelta(days=7)
            end = now
        elif time_range == TimeRange.MONTH:
            start = now - timedelta(days=30)
            end = now
        elif time_range == TimeRange.QUARTER:
            start = now - timedelta(days=90)
            end = now
        elif time_range == TimeRange.YEAR:
            start = now - timedelta(days=365)
            end = now
        else:
            # Default to week
            start = now - timedelta(days=7)
            end = now
        
        return start, end
    
    async def get_kpis(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> AnalyticsKPIResponse:
        """Get KPI metrics with trend analysis"""
        
        # Get current period date range
        current_start, current_end = self._get_date_range(time_range, start_date, end_date)
        
        # Calculate previous period date range (same duration)
        period_duration = current_end - current_start
        previous_start = current_start - period_duration
        previous_end = current_start
        
        # Total Bookings
        current_bookings = await self._count_bookings(current_start, current_end)
        previous_bookings = await self._count_bookings(previous_start, previous_end)
        bookings_change = self._calculate_change(current_bookings, previous_bookings)
        
        # Total Revenue
        current_revenue = await self._sum_revenue(current_start, current_end)
        previous_revenue = await self._sum_revenue(previous_start, previous_end)
        revenue_change = self._calculate_change(current_revenue, previous_revenue)
        
        # Active Complaints
        current_complaints = await self._count_active_complaints()
        previous_complaints = await self._count_complaints(previous_start, previous_end)
        complaints_change = self._calculate_change(current_complaints, previous_complaints)
        
        # Average Resolution Time
        current_resolution_time = await self._avg_resolution_time(current_start, current_end)
        previous_resolution_time = await self._avg_resolution_time(previous_start, previous_end)
        resolution_change = self._calculate_change(current_resolution_time, previous_resolution_time)
        
        # Customer Satisfaction (mock for now - requires ratings table)
        current_satisfaction = 4.6
        previous_satisfaction = 4.4
        satisfaction_change = self._calculate_change(current_satisfaction, previous_satisfaction)
        
        # Staff Utilization (mock for now - requires staff activity tracking)
        current_utilization = 87.0
        previous_utilization = 84.5
        utilization_change = self._calculate_change(current_utilization, previous_utilization)
        
        return AnalyticsKPIResponse(
            total_bookings=KPIMetric(
                value=current_bookings,
                change=bookings_change,
                trend="up" if bookings_change >= 0 else "down"
            ),
            total_revenue=KPIMetric(
                value=current_revenue,
                change=revenue_change,
                trend="up" if revenue_change >= 0 else "down"
            ),
            active_complaints=KPIMetric(
                value=current_complaints,
                change=complaints_change,
                trend="down" if complaints_change <= 0 else "up"  # Lower is better
            ),
            avg_resolution_time=KPIMetric(
                value=current_resolution_time,
                change=resolution_change,
                trend="down" if resolution_change <= 0 else "up"  # Lower is better
            ),
            customer_satisfaction=KPIMetric(
                value=current_satisfaction,
                change=satisfaction_change,
                trend="up" if satisfaction_change >= 0 else "down"
            ),
            staff_utilization=KPIMetric(
                value=current_utilization,
                change=utilization_change,
                trend="up" if utilization_change >= 0 else "down"
            )
        )
    
    async def get_trends(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> AnalyticsTrendResponse:
        """Get trend data for charts"""
        
        start, end = self._get_date_range(time_range, start_date, end_date)
        
        # Determine grouping based on time range
        if time_range == TimeRange.TODAY:
            # Group by hour
            date_format = "%H:00"
            interval_hours = 1
        elif time_range == TimeRange.WEEK:
            # Group by day
            date_format = "%a"  # Mon, Tue, etc.
            interval_hours = 24
        else:
            # Group by day for month/quarter/year
            date_format = "%m-%d"
            interval_hours = 24
        
        # Get bookings grouped by date
        trend_data = []
        current = start
        
        while current < end:
            next_period = current + timedelta(hours=interval_hours)
            
            bookings_count = await self._count_bookings(current, next_period)
            revenue_sum = await self._sum_revenue(current, next_period)
            complaints_count = await self._count_complaints(current, next_period)
            
            trend_data.append(TrendDataPoint(
                date=current.strftime(date_format),
                bookings=bookings_count,
                revenue=revenue_sum,
                complaints=complaints_count
            ))
            
            current = next_period
        
        return AnalyticsTrendResponse(data=trend_data)
    
    async def get_category_distribution(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> AnalyticsCategoryResponse:
        """Get service category distribution"""
        
        start, end = self._get_date_range(time_range, start_date, end_date)
        
        # Query bookings grouped by category
        query = (
            select(
                Category.name,
                func.count(Booking.id).label('count')
            )
            .join(Booking, Booking.category_id == Category.id)
            .where(
                and_(
                    Booking.created_at >= start,
                    Booking.created_at <= end
                )
            )
            .group_by(Category.name)
            .order_by(func.count(Booking.id).desc())
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # Calculate total and percentages
        total = sum(row.count for row in rows)
        
        category_data = []
        for row in rows:
            percentage = (row.count / total * 100) if total > 0 else 0
            category_data.append(CategoryData(
                name=row.name,
                value=row.count,
                percentage=round(percentage, 1)
            ))
        
        return AnalyticsCategoryResponse(data=category_data)
    
    async def get_status_distribution(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> AnalyticsStatusResponse:
        """Get booking status distribution"""
        
        start, end = self._get_date_range(time_range, start_date, end_date)
        
        # Status color mapping
        status_colors = {
            "COMPLETED": "#10B981",
            "IN_PROGRESS": "#3B82F6",
            "CONFIRMED": "#3B82F6",
            "PENDING": "#F59E0B",
            "CANCELLED": "#EF4444"
        }
        
        # Query bookings grouped by status
        query = (
            select(
                Booking.status,
                func.count(Booking.id).label('count')
            )
            .where(
                and_(
                    Booking.created_at >= start,
                    Booking.created_at <= end
                )
            )
            .group_by(Booking.status)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        status_data = []
        for row in rows:
            status_name = row.status.replace('_', ' ').title()
            color = status_colors.get(row.status, "#9CA3AF")
            
            status_data.append(StatusData(
                name=status_name,
                value=row.count,
                color=color
            ))
        
        return AnalyticsStatusResponse(data=status_data)
    
    async def get_performance_metrics(
        self, 
        time_range: TimeRange, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> AnalyticsPerformanceResponse:
        """Get performance metrics vs targets"""
        
        # TODO: Implement actual performance calculations
        # For now, returning mock data with realistic values
        
        metrics = [
            PerformanceMetric(metric="Response Time", current=85.0, target=90.0),
            PerformanceMetric(metric="Resolution Rate", current=92.0, target=95.0),
            PerformanceMetric(metric="Customer Satisfaction", current=88.0, target=85.0),
            PerformanceMetric(metric="Staff Efficiency", current=87.0, target=80.0),
            PerformanceMetric(metric="SLA Compliance", current=94.0, target=95.0)
        ]
        
        return AnalyticsPerformanceResponse(data=metrics)
    
    # Helper methods
    
    async def _count_bookings(self, start: datetime, end: datetime) -> int:
        """Count bookings in date range"""
        query = select(func.count(Booking.id)).where(
            and_(
                Booking.created_at >= start,
                Booking.created_at <= end
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _sum_revenue(self, start: datetime, end: datetime) -> float:
        """Sum revenue in date range"""
        query = select(func.sum(Booking.total)).where(
            and_(
                Booking.created_at >= start,
                Booking.created_at <= end,
                Booking.status.in_(['COMPLETED', 'IN_PROGRESS', 'CONFIRMED'])
            )
        )
        result = await self.db.execute(query)
        return float(result.scalar() or 0)
    
    async def _count_active_complaints(self) -> int:
        """Count active complaints"""
        query = select(func.count(Complaint.id)).where(
            Complaint.status.in_(['OPEN', 'IN_PROGRESS', 'ESCALATED'])
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_complaints(self, start: datetime, end: datetime) -> int:
        """Count complaints in date range"""
        query = select(func.count(Complaint.id)).where(
            and_(
                Complaint.created_at >= start,
                Complaint.created_at <= end
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _avg_resolution_time(self, start: datetime, end: datetime) -> float:
        """Calculate average resolution time in hours"""
        query = select(
            func.avg(
                func.timestampdiff(
                    'HOUR',
                    Complaint.created_at,
                    Complaint.resolved_at
                )
            )
        ).where(
            and_(
                Complaint.created_at >= start,
                Complaint.created_at <= end,
                Complaint.status == 'RESOLVED',
                Complaint.resolved_at.isnot(None)
            )
        )
        result = await self.db.execute(query)
        avg_time = result.scalar()
        return float(avg_time) if avg_time else 0.0
    
    def _calculate_change(self, current: float, previous: float) -> float:
        """Calculate percentage change"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        change = ((current - previous) / previous) * 100
        return round(change, 1)

