"""
Metrics Schemas
Pydantic schemas for operational metrics and dashboard statistics.
"""

from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field


class BookingsMetrics(BaseModel):
    """Bookings statistics"""
    
    by_status: Dict[str, int] = Field(
        ...,
        description="Bookings count grouped by status",
        example={
            "pending": 15,
            "confirmed": 23,
            "in_progress": 12,
            "completed": 145,
            "cancelled": 8
        }
    )
    today: int = Field(..., description="Today's bookings count", example=15)
    week: int = Field(..., description="This week's bookings count", example=87)
    month: int = Field(..., description="This month's bookings count", example=342)
    growth_rate: float = Field(
        ...,
        description="Growth rate percentage vs previous period",
        example=12.5
    )


class ComplaintsMetrics(BaseModel):
    """Complaints statistics"""
    
    by_priority: Dict[str, int] = Field(
        ...,
        description="Complaints count grouped by priority",
        example={
            "low": 45,
            "medium": 32,
            "high": 18,
            "critical": 5
        }
    )
    by_status: Dict[str, int] = Field(
        ...,
        description="Complaints count grouped by status",
        example={
            "open": 23,
            "in_progress": 15,
            "resolved": 45,
            "closed": 12,
            "escalated": 5
        }
    )
    today: int = Field(..., description="Today's complaints count", example=8)
    unresolved: int = Field(
        ...,
        description="Unresolved complaints count (open, in_progress, escalated)",
        example=43
    )
    avg_resolution_hours: Optional[float] = Field(
        None,
        description="Average resolution time in hours",
        example=18.5
    )


class SLAMetrics(BaseModel):
    """SLA compliance metrics"""
    
    at_risk: int = Field(
        ...,
        description="Complaints at risk of SLA breach (within buffer time)",
        example=5
    )
    breached: int = Field(
        ...,
        description="Complaints with breached SLA",
        example=2
    )
    compliance_rate: float = Field(
        ...,
        description="SLA compliance rate percentage",
        example=94.2
    )
    avg_response_hours: Optional[float] = Field(
        None,
        description="Average response time in hours",
        example=2.3
    )
    avg_resolution_hours: Optional[float] = Field(
        None,
        description="Average resolution time in hours",
        example=18.5
    )


class RevenueMetrics(BaseModel):
    """Revenue statistics"""
    
    total: float = Field(
        ...,
        description="Total revenue for period (paid bookings only)",
        example=1250000.00
    )
    by_status: Dict[str, float] = Field(
        ...,
        description="Revenue grouped by booking status",
        example={
            "pending": 0.0,
            "confirmed": 0.0,
            "in_progress": 45000.00,
            "completed": 1205000.00,
            "cancelled": 0.0
        }
    )
    today: float = Field(..., description="Today's revenue", example=45000.00)
    week: float = Field(..., description="This week's revenue", example=285000.00)
    month: float = Field(..., description="This month's revenue", example=1250000.00)
    average_order_value: float = Field(
        ...,
        description="Average order value",
        example=3654.76
    )
    growth_rate: float = Field(
        ...,
        description="Revenue growth rate percentage vs previous period",
        example=8.3
    )


class StaffWorkloadItem(BaseModel):
    """Individual staff workload"""
    
    staff_id: int = Field(..., description="Staff member ID", example=1)
    staff_name: str = Field(..., description="Staff member name", example="John Doe")
    assigned_complaints: int = Field(
        ...,
        description="Number of assigned active complaints",
        example=5
    )


class StaffWorkload(BaseModel):
    """Staff workload statistics"""
    
    total_staff: int = Field(..., description="Total number of staff members", example=8)
    staff_assignments: List[StaffWorkloadItem] = Field(
        ...,
        description="Individual staff assignments"
    )


class RealtimeMetrics(BaseModel):
    """Real-time dashboard statistics"""
    
    active_bookings: int = Field(
        ...,
        description="Active bookings count (in_progress)",
        example=12
    )
    pending_bookings: int = Field(
        ...,
        description="Pending bookings count (pending, confirmed)",
        example=38
    )
    active_complaints: int = Field(
        ...,
        description="Active complaints count (open, in_progress)",
        example=38
    )
    critical_complaints: int = Field(
        ...,
        description="Critical priority complaints count",
        example=5
    )
    staff_workload: Dict[str, Any] = Field(
        ...,
        description="Staff workload statistics"
    )


class DashboardMetricsResponse(BaseModel):
    """Complete dashboard metrics response"""
    
    period: str = Field(
        ...,
        description="Time period for metrics",
        example="all"
    )
    generated_at: str = Field(
        ...,
        description="Timestamp when metrics were generated (ISO 8601)",
        example="2025-10-15T10:30:00Z"
    )
    bookings: Optional[BookingsMetrics] = Field(
        None,
        description="Bookings metrics (if requested)"
    )
    complaints: Optional[ComplaintsMetrics] = Field(
        None,
        description="Complaints metrics (if requested)"
    )
    sla: Optional[SLAMetrics] = Field(
        None,
        description="SLA metrics (if requested)"
    )
    revenue: Optional[RevenueMetrics] = Field(
        None,
        description="Revenue metrics (if requested)"
    )
    realtime: Optional[RealtimeMetrics] = Field(
        None,
        description="Real-time metrics (if requested)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "all",
                "generated_at": "2025-10-15T10:30:00Z",
                "bookings": {
                    "by_status": {
                        "pending": 15,
                        "confirmed": 23,
                        "in_progress": 12,
                        "completed": 145,
                        "cancelled": 8
                    },
                    "today": 15,
                    "week": 87,
                    "month": 342,
                    "growth_rate": 12.5
                },
                "complaints": {
                    "by_priority": {
                        "low": 45,
                        "medium": 32,
                        "high": 18,
                        "critical": 5
                    },
                    "by_status": {
                        "open": 23,
                        "in_progress": 15,
                        "resolved": 45,
                        "closed": 12,
                        "escalated": 5
                    },
                    "today": 8,
                    "unresolved": 43,
                    "avg_resolution_hours": 18.5
                },
                "sla": {
                    "at_risk": 5,
                    "breached": 2,
                    "compliance_rate": 94.2,
                    "avg_response_hours": 2.3,
                    "avg_resolution_hours": 18.5
                },
                "revenue": {
                    "total": 1250000.00,
                    "by_status": {
                        "pending": 0.0,
                        "confirmed": 0.0,
                        "in_progress": 45000.00,
                        "completed": 1205000.00,
                        "cancelled": 0.0
                    },
                    "today": 45000.00,
                    "week": 285000.00,
                    "month": 1250000.00,
                    "average_order_value": 3654.76,
                    "growth_rate": 8.3
                },
                "realtime": {
                    "active_bookings": 12,
                    "pending_bookings": 38,
                    "active_complaints": 38,
                    "critical_complaints": 5,
                    "staff_workload": {
                        "total_staff": 8,
                        "staff_assignments": [
                            {
                                "staff_id": 1,
                                "staff_name": "John Doe",
                                "assigned_complaints": 5
                            }
                        ]
                    }
                }
            }
        }

