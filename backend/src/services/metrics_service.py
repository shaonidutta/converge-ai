"""
Metrics Service
Business logic for operational metrics and dashboard statistics.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.metrics_repository import MetricsRepository
from src.services.config_service import ConfigService
from src.services.audit_service import AuditService


class MetricsService:
    """Service for operational metrics and statistics"""
    
    def __init__(
        self,
        db: AsyncSession,
        config_service: ConfigService,
        audit_service: AuditService
    ):
        """
        Initialize metrics service
        
        Args:
            db: Database session
            config_service: Configuration service
            audit_service: Audit service
        """
        self.db = db
        self.repository = MetricsRepository(db)
        self.config_service = config_service
        self.audit_service = audit_service
    
    async def get_dashboard_metrics(
        self,
        staff_id: int,
        period: str = "all",
        include_groups: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics

        Args:
            staff_id: Staff member ID (for audit logging)
            period: Time period ("today", "week", "month", "all")
            include_groups: List of metric groups to include
                           (bookings, complaints, sla, revenue, realtime)
                           If None, includes all groups

        Returns:
            Dictionary with requested metrics
        """
        import asyncio

        # Default to all groups if not specified
        if include_groups is None:
            include_groups = ["bookings", "complaints", "sla", "revenue", "realtime"]

        # Initialize response
        response = {
            "period": period,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        # Prepare tasks for parallel execution
        tasks = []
        task_names = []

        if "bookings" in include_groups:
            tasks.append(self._get_bookings_metrics(period))
            task_names.append("bookings")

        if "complaints" in include_groups:
            tasks.append(self._get_complaints_metrics(period))
            task_names.append("complaints")

        if "sla" in include_groups:
            tasks.append(self._get_sla_metrics(period))
            task_names.append("sla")

        if "revenue" in include_groups:
            tasks.append(self._get_revenue_metrics(period))
            task_names.append("revenue")

        if "realtime" in include_groups:
            tasks.append(self._get_realtime_metrics())
            task_names.append("realtime")

        # Execute all metric queries in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Log error but continue with other metrics
                    print(f"Error getting {task_names[i]} metrics: {result}")
                    response[task_names[i]] = {"error": "Failed to retrieve metrics"}
                else:
                    response[task_names[i]] = result

        # Log metrics access (run in parallel with metrics gathering)
        await self.audit_service.log_access(
            staff_id=staff_id,
            action="view_metrics",
            resource_type="dashboard_metrics",
            resource_id=None,
            pii_accessed=False,
            request_metadata={
                "period": period,
                "include_groups": include_groups
            }
        )

        return response
    
    async def _get_bookings_metrics(self, period: str) -> Dict[str, Any]:
        """
        Get bookings metrics

        Args:
            period: Time period filter

        Returns:
            Bookings metrics dictionary
        """
        import asyncio

        # Run all booking queries in parallel
        by_status_task = self.repository.get_bookings_by_status(period)
        today_count_task = self.repository.get_bookings_count("today")
        week_count_task = self.repository.get_bookings_count("week")
        month_count_task = self.repository.get_bookings_count("month")

        # Execute all queries in parallel
        by_status, today_count, week_count, month_count = await asyncio.gather(
            by_status_task,
            today_count_task,
            week_count_task,
            month_count_task,
            return_exceptions=True
        )

        # Handle any exceptions
        if isinstance(by_status, Exception):
            by_status = {}
        if isinstance(today_count, Exception):
            today_count = 0
        if isinstance(week_count, Exception):
            week_count = 0
        if isinstance(month_count, Exception):
            month_count = 0

        # Calculate growth rate (current month vs previous month)
        # For simplicity, we'll calculate growth based on available data
        # In production, you'd query previous month's data
        growth_rate = 0.0  # Placeholder - would need historical data

        return {
            "by_status": by_status,
            "today": today_count,
            "week": week_count,
            "month": month_count,
            "growth_rate": growth_rate
        }
    
    async def _get_complaints_metrics(self, period: str) -> Dict[str, Any]:
        """
        Get complaints metrics

        Args:
            period: Time period filter

        Returns:
            Complaints metrics dictionary
        """
        import asyncio

        # Run all complaint queries in parallel
        by_priority_task = self.repository.get_complaints_by_priority(period)
        by_status_task = self.repository.get_complaints_by_status(period)
        today_count_task = self.repository.get_complaints_count("today")
        unresolved_count_task = self.repository.get_unresolved_complaints_count()
        avg_resolution_task = self.repository.get_average_resolution_time(period)

        # Execute all queries in parallel
        results = await asyncio.gather(
            by_priority_task,
            by_status_task,
            today_count_task,
            unresolved_count_task,
            avg_resolution_task,
            return_exceptions=True
        )

        # Handle any exceptions
        by_priority = results[0] if not isinstance(results[0], Exception) else {}
        by_status = results[1] if not isinstance(results[1], Exception) else {}
        today_count = results[2] if not isinstance(results[2], Exception) else 0
        unresolved_count = results[3] if not isinstance(results[3], Exception) else 0
        avg_resolution_hours = results[4] if not isinstance(results[4], Exception) else 0.0

        return {
            "by_priority": by_priority,
            "by_status": by_status,
            "today": today_count,
            "unresolved": unresolved_count,
            "avg_resolution_hours": avg_resolution_hours
        }
    
    async def _get_sla_metrics(self, period: str) -> Dict[str, Any]:
        """
        Get SLA compliance metrics
        
        Args:
            period: Time period filter
            
        Returns:
            SLA metrics dictionary
        """
        # Get SLA buffer hours from config
        buffer_hours = await self.config_service.get_config_int("SLA_BUFFER_HOURS", 1)
        
        # Get SLA counts
        at_risk_count = await self.repository.get_sla_at_risk_count(buffer_hours)
        breached_count = await self.repository.get_sla_breached_count()
        
        # Get total active complaints for compliance rate
        active_complaints = await self.repository.get_active_complaints_count()
        total_complaints = await self.repository.get_complaints_count(period)
        
        # Calculate compliance rate
        if total_complaints > 0:
            # Compliance = (total - breached) / total * 100
            compliance_rate = round(
                ((total_complaints - breached_count) / total_complaints) * 100,
                2
            )
        else:
            compliance_rate = 100.0
        
        # Get average resolution time
        avg_resolution_hours = await self.repository.get_average_resolution_time(period)
        
        # For avg_response_hours, we'd need to track response timestamps
        # Placeholder for now
        avg_response_hours = None
        
        return {
            "at_risk": at_risk_count,
            "breached": breached_count,
            "compliance_rate": compliance_rate,
            "avg_response_hours": avg_response_hours,
            "avg_resolution_hours": avg_resolution_hours
        }
    
    async def _get_revenue_metrics(self, period: str) -> Dict[str, Any]:
        """
        Get revenue metrics
        
        Args:
            period: Time period filter
            
        Returns:
            Revenue metrics dictionary
        """
        # Get revenue by status
        by_status = await self.repository.get_revenue_by_status(period)
        
        # Get revenue for different periods
        total_revenue = await self.repository.get_total_revenue(period)
        today_revenue = await self.repository.get_total_revenue("today")
        week_revenue = await self.repository.get_total_revenue("week")
        month_revenue = await self.repository.get_total_revenue("month")
        
        # Get average order value
        avg_order_value = await self.repository.get_average_order_value(period)
        
        # Calculate growth rate (placeholder)
        growth_rate = 0.0
        
        return {
            "total": total_revenue,
            "by_status": by_status,
            "today": today_revenue,
            "week": week_revenue,
            "month": month_revenue,
            "average_order_value": avg_order_value,
            "growth_rate": growth_rate
        }
    
    async def _get_realtime_metrics(self) -> Dict[str, Any]:
        """
        Get real-time dashboard statistics
        
        Returns:
            Real-time metrics dictionary
        """
        # Get real-time counts
        active_bookings = await self.repository.get_active_bookings_count()
        pending_bookings = await self.repository.get_pending_bookings_count()
        active_complaints = await self.repository.get_active_complaints_count()
        critical_complaints = await self.repository.get_critical_complaints_count()
        
        # Get staff workload
        staff_workload = await self.repository.get_staff_workload()
        
        return {
            "active_bookings": active_bookings,
            "pending_bookings": pending_bookings,
            "active_complaints": active_complaints,
            "critical_complaints": critical_complaints,
            "staff_workload": staff_workload
        }
    
    def _calculate_growth_rate(
        self,
        current: float,
        previous: float
    ) -> float:
        """
        Calculate growth rate percentage
        
        Args:
            current: Current period value
            previous: Previous period value
            
        Returns:
            Growth rate percentage
        """
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        
        growth = ((current - previous) / previous) * 100
        return round(growth, 2)

