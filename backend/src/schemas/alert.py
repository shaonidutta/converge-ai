"""
Alert Schemas
Pydantic models for alert API requests and responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Alert Schemas
# ============================================================================

class AlertResponse(BaseModel):
    """Alert response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    alert_type: str = Field(..., description="Alert type (sla_breach, critical_complaint, etc.)")
    severity: str = Field(..., description="Severity level (info, warning, critical)")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    resource_type: Optional[str] = Field(None, description="Related resource type")
    resource_id: Optional[int] = Field(None, description="Related resource ID")
    assigned_to_staff_id: Optional[int] = Field(None, description="Assigned staff ID")
    is_read: bool = Field(..., description="Whether alert has been read")
    is_dismissed: bool = Field(..., description="Whether alert has been dismissed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional alert data")
    created_at: datetime = Field(..., description="Alert creation time")
    read_at: Optional[datetime] = Field(None, description="When alert was read")
    dismissed_at: Optional[datetime] = Field(None, description="When alert was dismissed")
    expires_at: Optional[datetime] = Field(None, description="When alert expires")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "alert_type": "sla_breach",
                "severity": "critical",
                "title": "CRITICAL: SLA Breach - Complaint #123",
                "message": "Complaint #123 has breached SLA deadline. Immediate action required.",
                "resource_type": "complaint",
                "resource_id": 123,
                "assigned_to_staff_id": 5,
                "is_read": False,
                "is_dismissed": False,
                "metadata": {"priority": "CRITICAL"},
                "created_at": "2025-10-15T10:30:00Z",
                "read_at": None,
                "dismissed_at": None,
                "expires_at": "2025-10-17T10:30:00Z"
            }
        }
    )


class AlertListResponse(BaseModel):
    """Paginated alert list response"""
    alerts: List[AlertResponse] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    unread_count: int = Field(..., description="Count of unread alerts")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alerts": [
                    {
                        "id": 1,
                        "alert_type": "sla_breach",
                        "severity": "critical",
                        "title": "CRITICAL: SLA Breach - Complaint #123",
                        "message": "Complaint #123 has breached SLA deadline.",
                        "resource_type": "complaint",
                        "resource_id": 123,
                        "assigned_to_staff_id": 5,
                        "is_read": False,
                        "is_dismissed": False,
                        "metadata": {},
                        "created_at": "2025-10-15T10:30:00Z",
                        "read_at": None,
                        "dismissed_at": None,
                        "expires_at": "2025-10-17T10:30:00Z"
                    }
                ],
                "total": 25,
                "page": 1,
                "page_size": 20,
                "total_pages": 2,
                "unread_count": 15
            }
        }
    )


class UnreadCountResponse(BaseModel):
    """Unread alert count response"""
    unread_count: int = Field(..., description="Number of unread alerts")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "unread_count": 15
            }
        }
    )


# ============================================================================
# Alert Rule Schemas
# ============================================================================

class AlertRuleCreate(BaseModel):
    """Create alert rule request"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="Unique rule name")
    rule_type: str = Field(..., description="Rule type (sla, threshold, event)")
    conditions: Dict[str, Any] = Field(..., description="Rule conditions (JSON)")
    alert_config: Dict[str, Any] = Field(..., description="Alert configuration (JSON)")
    is_enabled: bool = Field(True, description="Whether rule is active")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_name": "high_workload_alert",
                "rule_type": "threshold",
                "conditions": {
                    "metric": "assigned_complaints",
                    "threshold": 10,
                    "operator": "greater_than"
                },
                "alert_config": {
                    "alert_type": "high_workload",
                    "severity": "warning",
                    "title_template": "High Workload Alert",
                    "message_template": "You have {count} assigned complaints.",
                    "assign_to_staff": True
                },
                "is_enabled": True
            }
        }
    )


class AlertRuleUpdate(BaseModel):
    """Update alert rule request"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_type: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    alert_config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class AlertRuleResponse(BaseModel):
    """Alert rule response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rule_name: str
    rule_type: str
    is_enabled: bool
    conditions: Dict[str, Any]
    alert_config: Dict[str, Any]
    created_by_staff_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "rule_name": "sla_breach_critical",
                "rule_type": "sla",
                "is_enabled": True,
                "conditions": {
                    "priority": "CRITICAL",
                    "buffer_hours": 1
                },
                "alert_config": {
                    "alert_type": "sla_breach",
                    "severity": "critical",
                    "title_template": "CRITICAL: SLA Breach for Complaint #{resource_id}",
                    "message_template": "Complaint #{resource_id} has breached SLA deadline."
                },
                "created_by_staff_id": 1,
                "created_at": "2025-10-15T10:00:00Z",
                "updated_at": "2025-10-15T10:00:00Z"
            }
        }
    )


# ============================================================================
# Alert Subscription Schemas
# ============================================================================

class AlertSubscriptionUpdate(BaseModel):
    """Update alert subscription request"""
    alert_type: str = Field(..., description="Alert type to subscribe to")
    is_enabled: bool = Field(..., description="Whether subscription is active")
    delivery_channels: Optional[List[str]] = Field(
        None,
        description="Delivery channels (in_app, email, sms)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_type": "sla_breach",
                "is_enabled": True,
                "delivery_channels": ["in_app", "email"]
            }
        }
    )


class AlertSubscriptionResponse(BaseModel):
    """Alert subscription response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    staff_id: int
    alert_type: str
    is_enabled: bool
    delivery_channels: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "staff_id": 5,
                "alert_type": "sla_breach",
                "is_enabled": True,
                "delivery_channels": ["in_app", "email"],
                "created_at": "2025-10-15T10:00:00Z",
                "updated_at": "2025-10-15T10:00:00Z"
            }
        }
    )


class AlertSubscriptionListResponse(BaseModel):
    """List of alert subscriptions"""
    subscriptions: List[AlertSubscriptionResponse] = Field(..., description="List of subscriptions")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subscriptions": [
                    {
                        "id": 1,
                        "staff_id": 5,
                        "alert_type": "sla_breach",
                        "is_enabled": True,
                        "delivery_channels": ["in_app", "email"],
                        "created_at": "2025-10-15T10:00:00Z",
                        "updated_at": "2025-10-15T10:00:00Z"
                    }
                ]
            }
        }
    )

