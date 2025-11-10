"""
Alert Routes
API endpoints for alert management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional, List

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_staff
from src.core.models.staff import Staff
from src.services.alert_service import AlertService
from src.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    UnreadCountResponse,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertSubscriptionUpdate,
    AlertSubscriptionResponse,
    AlertSubscriptionListResponse
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ============================================================================
# Alert Endpoints
# ============================================================================

@router.get(
    "",
    response_model=AlertListResponse,
    summary="Get staff alerts"
)
async def get_alerts(
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)],
    unread_only: bool = Query(False, description="Show only unread alerts"),
    alert_types: Optional[str] = Query(None, description="Comma-separated alert types"),
    severities: Optional[str] = Query(None, description="Comma-separated severities (info,warning,critical)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get alerts for the current staff member
    
    **Permissions Required:** alerts.read
    
    **Query Parameters:**
    - unread_only: Filter to show only unread alerts
    - alert_types: Filter by alert types (comma-separated)
    - severities: Filter by severity levels (comma-separated)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    **Returns:**
    - Paginated list of alerts
    - Total count and unread count
    """
    try:
        alert_service = AlertService(db)
        
        # Parse filters
        alert_type_list = alert_types.split(',') if alert_types else None
        severity_list = severities.split(',') if severities else None
        
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Get alerts
        alerts, total = await alert_service.get_staff_alerts(
            staff_id=current_staff.id,
            unread_only=unread_only,
            alert_types=alert_type_list,
            severities=severity_list,
            skip=skip,
            limit=page_size
        )
        
        # Get unread count
        unread_count = await alert_service.get_unread_count(current_staff.id)
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return AlertListResponse(
            alerts=[AlertResponse.model_validate(alert) for alert in alerts],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            unread_count=unread_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )


@router.get(
    "/unread/count",
    response_model=UnreadCountResponse,
    summary="Get unread alert count"
)
async def get_unread_count(
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get count of unread alerts for current staff

    **Permissions Required:** alerts.read

    **Returns:**
    - Count of unread alerts
    """
    try:
        alert_service = AlertService(db)
        count = await alert_service.get_unread_count(current_staff.id)

        return UnreadCountResponse(unread_count=count)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


# ============================================================================
# Alert Rule Endpoints (Admin Only)
# ============================================================================

@router.get(
    "/rules",
    response_model=List[AlertRuleResponse],
    summary="Get alert rules"
)
async def get_alert_rules(
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)],
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    enabled_only: bool = Query(True, description="Show only enabled rules")
):
    """
    Get all alert rules (admin only)

    **Permissions Required:** alerts.manage
    """
    try:
        alert_service = AlertService(db)
        rules = await alert_service.alert_repo.get_alert_rules(
            rule_type=rule_type,
            enabled_only=enabled_only
        )

        return [AlertRuleResponse.model_validate(rule) for rule in rules]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alert rules: {str(e)}"
        )


@router.get(
    "/subscriptions",
    response_model=AlertSubscriptionListResponse,
    summary="Get alert subscriptions"
)
async def get_subscriptions(
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get alert subscriptions for current staff

    **Permissions Required:** alerts.read
    """
    try:
        alert_service = AlertService(db)
        subscriptions = await alert_service.alert_repo.get_subscriptions_for_staff(current_staff.id)

        return AlertSubscriptionListResponse(
            subscriptions=[AlertSubscriptionResponse.model_validate(sub) for sub in subscriptions]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscriptions: {str(e)}"
        )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get single alert"
)
async def get_alert(
    alert_id: int,
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get a single alert by ID

    **Permissions Required:** alerts.read

    **Returns:**
    - Alert details
    """
    try:
        alert_service = AlertService(db)
        alert = await alert_service.alert_repo.get_alert_by_id(alert_id)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found"
            )

        # Verify ownership
        if alert.assigned_to_staff_id != current_staff.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this alert"
            )

        return AlertResponse.model_validate(alert)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alert: {str(e)}"
        )


@router.put(
    "/{alert_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark alert as read"
)
async def mark_alert_read(
    alert_id: int,
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Mark an alert as read
    
    **Permissions Required:** alerts.read
    """
    try:
        alert_service = AlertService(db)
        success = await alert_service.mark_alert_read(alert_id, current_staff.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found or not assigned to you"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark alert as read: {str(e)}"
        )


@router.put(
    "/{alert_id}/dismiss",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dismiss alert"
)
async def dismiss_alert(
    alert_id: int,
    current_staff: Annotated[Staff, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Dismiss an alert
    
    **Permissions Required:** alerts.read
    """
    try:
        alert_service = AlertService(db)
        success = await alert_service.dismiss_alert(alert_id, current_staff.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found or not assigned to you"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dismiss alert: {str(e)}"
        )
