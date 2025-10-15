"""
Metrics Repository
Handles database queries for operational metrics and statistics.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import func, case, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models.booking import Booking, BookingStatus, PaymentStatus
from src.core.models.complaint import Complaint, ComplaintPriority, ComplaintStatus
from src.core.models.staff import Staff


class MetricsRepository:
    """Repository for metrics and statistics queries"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize metrics repository
        
        Args:
            db: Database session
        """
        self.db = db
    
    def _get_period_filter(self, period: str) -> Optional[datetime]:
        """
        Get datetime filter for period
        
        Args:
            period: Period string ("today", "week", "month", "all")
            
        Returns:
            Datetime threshold or None for "all"
        """
        now = datetime.utcnow()
        
        if period == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            return now - timedelta(days=7)
        elif period == "month":
            return now - timedelta(days=30)
        else:  # "all"
            return None
    
    async def get_bookings_by_status(self, period: str = "all") -> Dict[str, int]:
        """
        Get bookings count grouped by status
        
        Args:
            period: Time period filter
            
        Returns:
            Dictionary with status counts
        """
        period_filter = self._get_period_filter(period)
        
        # Build query
        query = self.db.query(
            Booking.status,
            func.count(Booking.id).label('count')
        )
        
        # Apply period filter
        if period_filter:
            query = query.filter(Booking.created_at >= period_filter)
        
        # Group by status
        query = query.group_by(Booking.status)
        
        # Execute query
        result = await query.all()
        
        # Convert to dictionary
        status_counts = {status.value: 0 for status in BookingStatus}
        for row in result:
            status_counts[row.status.value] = row.count
        
        return status_counts
    
    async def get_bookings_count(self, period: str = "all") -> int:
        """
        Get total bookings count for period
        
        Args:
            period: Time period filter
            
        Returns:
            Total count
        """
        period_filter = self._get_period_filter(period)
        
        query = self.db.query(func.count(Booking.id))
        
        if period_filter:
            query = query.filter(Booking.created_at >= period_filter)
        
        result = await query.scalar()
        return result or 0
    
    async def get_complaints_by_priority(self, period: str = "all") -> Dict[str, int]:
        """
        Get complaints count grouped by priority
        
        Args:
            period: Time period filter
            
        Returns:
            Dictionary with priority counts
        """
        period_filter = self._get_period_filter(period)
        
        query = self.db.query(
            Complaint.priority,
            func.count(Complaint.id).label('count')
        )
        
        if period_filter:
            query = query.filter(Complaint.created_at >= period_filter)
        
        query = query.group_by(Complaint.priority)
        
        result = await query.all()
        
        priority_counts = {priority.value: 0 for priority in ComplaintPriority}
        for row in result:
            priority_counts[row.priority.value] = row.count
        
        return priority_counts
    
    async def get_complaints_by_status(self, period: str = "all") -> Dict[str, int]:
        """
        Get complaints count grouped by status
        
        Args:
            period: Time period filter
            
        Returns:
            Dictionary with status counts
        """
        period_filter = self._get_period_filter(period)
        
        query = self.db.query(
            Complaint.status,
            func.count(Complaint.id).label('count')
        )
        
        if period_filter:
            query = query.filter(Complaint.created_at >= period_filter)
        
        query = query.group_by(Complaint.status)
        
        result = await query.all()
        
        status_counts = {status.value: 0 for status in ComplaintStatus}
        for row in result:
            status_counts[row.status.value] = row.count
        
        return status_counts
    
    async def get_complaints_count(self, period: str = "all") -> int:
        """
        Get total complaints count for period
        
        Args:
            period: Time period filter
            
        Returns:
            Total count
        """
        period_filter = self._get_period_filter(period)
        
        query = self.db.query(func.count(Complaint.id))
        
        if period_filter:
            query = query.filter(Complaint.created_at >= period_filter)
        
        result = await query.scalar()
        return result or 0
    
    async def get_unresolved_complaints_count(self) -> int:
        """
        Get count of unresolved complaints (open, in_progress, escalated)
        
        Returns:
            Count of unresolved complaints
        """
        result = await self.db.query(func.count(Complaint.id)).filter(
            Complaint.status.in_([
                ComplaintStatus.OPEN,
                ComplaintStatus.IN_PROGRESS,
                ComplaintStatus.ESCALATED
            ])
        ).scalar()
        
        return result or 0
    
    async def get_average_resolution_time(self, period: str = "all") -> Optional[float]:
        """
        Get average complaint resolution time in hours
        
        Args:
            period: Time period filter
            
        Returns:
            Average resolution time in hours or None
        """
        period_filter = self._get_period_filter(period)
        
        query = self.db.query(
            func.avg(
                func.timestampdiff(
                    'SECOND',
                    Complaint.created_at,
                    Complaint.resolved_at
                )
            ).label('avg_seconds')
        ).filter(
            Complaint.resolved_at.isnot(None)
        )
        
        if period_filter:
            query = query.filter(Complaint.created_at >= period_filter)
        
        result = await query.scalar()
        
        if result:
            return round(result / 3600, 2)  # Convert seconds to hours
        return None
    
    async def get_sla_at_risk_count(self, buffer_hours: int = 1) -> int:
        """
        Get count of complaints at risk of SLA breach
        
        Args:
            buffer_hours: Hours before due date to consider at risk
            
        Returns:
            Count of at-risk complaints
        """
        now = datetime.utcnow()
        buffer_time = now + timedelta(hours=buffer_hours)
        
        result = await self.db.query(func.count(Complaint.id)).filter(
            and_(
                Complaint.status.in_([
                    ComplaintStatus.OPEN,
                    ComplaintStatus.IN_PROGRESS
                ]),
                or_(
                    and_(
                        Complaint.response_due_at.isnot(None),
                        Complaint.response_due_at <= buffer_time,
                        Complaint.response_due_at > now
                    ),
                    and_(
                        Complaint.resolution_due_at.isnot(None),
                        Complaint.resolution_due_at <= buffer_time,
                        Complaint.resolution_due_at > now
                    )
                )
            )
        ).scalar()
        
        return result or 0
    
    async def get_sla_breached_count(self) -> int:
        """
        Get count of complaints with breached SLA
        
        Returns:
            Count of breached complaints
        """
        now = datetime.utcnow()
        
        result = await self.db.query(func.count(Complaint.id)).filter(
            and_(
                Complaint.status.in_([
                    ComplaintStatus.OPEN,
                    ComplaintStatus.IN_PROGRESS
                ]),
                or_(
                    and_(
                        Complaint.response_due_at.isnot(None),
                        Complaint.response_due_at < now
                    ),
                    and_(
                        Complaint.resolution_due_at.isnot(None),
                        Complaint.resolution_due_at < now
                    )
                )
            )
        ).scalar()
        
        return result or 0

    async def get_revenue_by_status(self, period: str = "all") -> Dict[str, float]:
        """
        Get revenue grouped by booking status

        Args:
            period: Time period filter

        Returns:
            Dictionary with status revenue
        """
        period_filter = self._get_period_filter(period)

        query = self.db.query(
            Booking.status,
            func.sum(Booking.total).label('revenue')
        ).filter(
            Booking.payment_status == PaymentStatus.PAID
        )

        if period_filter:
            query = query.filter(Booking.created_at >= period_filter)

        query = query.group_by(Booking.status)

        result = await query.all()

        status_revenue = {status.value: 0.0 for status in BookingStatus}
        for row in result:
            status_revenue[row.status.value] = float(row.revenue or 0)

        return status_revenue

    async def get_total_revenue(self, period: str = "all") -> float:
        """
        Get total revenue for period (only paid bookings)

        Args:
            period: Time period filter

        Returns:
            Total revenue
        """
        period_filter = self._get_period_filter(period)

        query = self.db.query(func.sum(Booking.total)).filter(
            Booking.payment_status == PaymentStatus.PAID
        )

        if period_filter:
            query = query.filter(Booking.created_at >= period_filter)

        result = await query.scalar()
        return float(result or 0)

    async def get_average_order_value(self, period: str = "all") -> float:
        """
        Get average order value for period

        Args:
            period: Time period filter

        Returns:
            Average order value
        """
        period_filter = self._get_period_filter(period)

        query = self.db.query(func.avg(Booking.total)).filter(
            Booking.payment_status == PaymentStatus.PAID
        )

        if period_filter:
            query = query.filter(Booking.created_at >= period_filter)

        result = await query.scalar()
        return round(float(result or 0), 2)

    async def get_active_bookings_count(self) -> int:
        """
        Get count of active bookings (in_progress)

        Returns:
            Count of active bookings
        """
        result = await self.db.query(func.count(Booking.id)).filter(
            Booking.status == BookingStatus.IN_PROGRESS
        ).scalar()

        return result or 0

    async def get_pending_bookings_count(self) -> int:
        """
        Get count of pending bookings (pending, confirmed)

        Returns:
            Count of pending bookings
        """
        result = await self.db.query(func.count(Booking.id)).filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED
            ])
        ).scalar()

        return result or 0

    async def get_active_complaints_count(self) -> int:
        """
        Get count of active complaints (open, in_progress)

        Returns:
            Count of active complaints
        """
        result = await self.db.query(func.count(Complaint.id)).filter(
            Complaint.status.in_([
                ComplaintStatus.OPEN,
                ComplaintStatus.IN_PROGRESS
            ])
        ).scalar()

        return result or 0

    async def get_critical_complaints_count(self) -> int:
        """
        Get count of critical priority complaints

        Returns:
            Count of critical complaints
        """
        result = await self.db.query(func.count(Complaint.id)).filter(
            and_(
                Complaint.priority == ComplaintPriority.CRITICAL,
                Complaint.status.in_([
                    ComplaintStatus.OPEN,
                    ComplaintStatus.IN_PROGRESS,
                    ComplaintStatus.ESCALATED
                ])
            )
        ).scalar()

        return result or 0

    async def get_staff_workload(self) -> Dict[str, Any]:
        """
        Get staff workload statistics

        Returns:
            Dictionary with staff workload data
        """
        # Count assigned complaints per staff
        complaint_workload = await self.db.query(
            Staff.id,
            Staff.name,
            func.count(Complaint.id).label('assigned_complaints')
        ).outerjoin(
            Complaint,
            and_(
                Complaint.assigned_to_staff_id == Staff.id,
                Complaint.status.in_([
                    ComplaintStatus.OPEN,
                    ComplaintStatus.IN_PROGRESS
                ])
            )
        ).group_by(Staff.id, Staff.name).all()

        workload_data = {
            "total_staff": len(complaint_workload),
            "staff_assignments": [
                {
                    "staff_id": row.id,
                    "staff_name": row.name,
                    "assigned_complaints": row.assigned_complaints
                }
                for row in complaint_workload
            ]
        }

        return workload_data

