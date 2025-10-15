"""
Alert Service
Business logic for alert system
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.alert_repository import AlertRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.config_service import ConfigService
from src.services.audit_service import AuditService
from src.core.models.alert import Alert, AlertRule, AlertSubscription
from src.core.models.complaint import Complaint, ComplaintPriority, ComplaintStatus

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.metrics_repo = MetricsRepository(db)
        self.config_service = ConfigService(db)
        self.audit_service = AuditService(db)
    
    # ========================================================================
    # Alert Management
    # ========================================================================
    
    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        assigned_to_staff_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_hours: Optional[int] = None
    ) -> Alert:
        """
        Create a new alert
        
        Args:
            alert_type: Type of alert (sla_breach, critical_complaint, etc.)
            severity: Severity level (info, warning, critical)
            title: Alert title
            message: Alert message
            resource_type: Related resource type (complaint, booking, etc.)
            resource_id: Related resource ID
            assigned_to_staff_id: Staff member to assign (None for broadcast)
            metadata: Additional alert data
            expires_in_hours: Hours until alert expires (None for no expiration)
        
        Returns:
            Created Alert object
        """
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        alert = await self.alert_repo.create_alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            assigned_to_staff_id=assigned_to_staff_id,
            metadata=metadata,
            expires_at=expires_at
        )
        
        await self.db.commit()
        
        logger.info(
            f"Alert created: type={alert_type}, severity={severity}, "
            f"staff_id={assigned_to_staff_id}, resource={resource_type}:{resource_id}"
        )
        
        return alert
    
    async def get_staff_alerts(
        self,
        staff_id: int,
        unread_only: bool = False,
        alert_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Alert], int]:
        """
        Get alerts for a staff member
        
        Returns:
            Tuple of (alerts, total_count)
        """
        alerts, total = await self.alert_repo.get_alerts_for_staff(
            staff_id=staff_id,
            unread_only=unread_only,
            alert_types=alert_types,
            severities=severities,
            skip=skip,
            limit=limit
        )
        
        # Log access for audit
        await self.audit_service.log_access(
            staff_id=staff_id,
            action="view_alerts",
            resource_type="alert",
            pii_accessed=False,
            request_metadata={"unread_only": unread_only, "count": len(alerts)}
        )
        
        return alerts, total
    
    async def get_unread_count(self, staff_id: int) -> int:
        """Get count of unread alerts"""
        return await self.alert_repo.get_unread_count(staff_id)
    
    async def mark_alert_read(self, alert_id: int, staff_id: int) -> bool:
        """Mark alert as read"""
        success = await self.alert_repo.mark_as_read(alert_id, staff_id)
        
        if success:
            await self.db.commit()
            logger.info(f"Alert {alert_id} marked as read by staff {staff_id}")
        
        return success
    
    async def dismiss_alert(self, alert_id: int, staff_id: int) -> bool:
        """Dismiss alert"""
        success = await self.alert_repo.mark_as_dismissed(alert_id, staff_id)
        
        if success:
            await self.db.commit()
            logger.info(f"Alert {alert_id} dismissed by staff {staff_id}")
        
        return success
    
    # ========================================================================
    # Alert Generation - SLA Checks
    # ========================================================================
    
    async def check_sla_alerts(self) -> int:
        """
        Check for SLA breaches and at-risk complaints
        Creates alerts for complaints approaching or past SLA deadlines
        
        Returns:
            Number of alerts created
        """
        buffer_hours = await self.config_service.get_config_int("SLA_BUFFER_HOURS", 1)
        buffer_time = datetime.utcnow() + timedelta(hours=buffer_hours)
        
        alerts_created = 0
        
        # Get complaints at risk or breached
        from sqlalchemy import select, and_, or_
        
        # At-risk complaints (within buffer time)
        at_risk_query = select(Complaint).where(
            and_(
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS]),
                or_(
                    and_(
                        Complaint.response_due_at.isnot(None),
                        Complaint.response_due_at <= buffer_time,
                        Complaint.response_due_at > datetime.utcnow()
                    ),
                    and_(
                        Complaint.resolution_due_at.isnot(None),
                        Complaint.resolution_due_at <= buffer_time,
                        Complaint.resolution_due_at > datetime.utcnow()
                    )
                )
            )
        )
        
        result = await self.db.execute(at_risk_query)
        at_risk_complaints = result.scalars().all()
        
        for complaint in at_risk_complaints:
            # Check if alert already exists
            existing_alert = await self._check_existing_alert(
                alert_type="sla_at_risk",
                resource_type="complaint",
                resource_id=complaint.id
            )
            
            if not existing_alert:
                await self.create_alert(
                    alert_type="sla_at_risk",
                    severity="warning",
                    title=f"SLA At Risk: Complaint #{complaint.id}",
                    message=f"Complaint #{complaint.id} is approaching SLA deadline within {buffer_hours} hour(s).",
                    resource_type="complaint",
                    resource_id=complaint.id,
                    assigned_to_staff_id=complaint.assigned_to_staff_id,
                    metadata={"priority": complaint.priority.value if complaint.priority else None},
                    expires_in_hours=24
                )
                alerts_created += 1
        
        # Breached complaints (past deadline)
        breached_query = select(Complaint).where(
            and_(
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS]),
                or_(
                    and_(
                        Complaint.response_due_at.isnot(None),
                        Complaint.response_due_at < datetime.utcnow()
                    ),
                    and_(
                        Complaint.resolution_due_at.isnot(None),
                        Complaint.resolution_due_at < datetime.utcnow()
                    )
                )
            )
        )
        
        result = await self.db.execute(breached_query)
        breached_complaints = result.scalars().all()
        
        for complaint in breached_complaints:
            existing_alert = await self._check_existing_alert(
                alert_type="sla_breach",
                resource_type="complaint",
                resource_id=complaint.id
            )
            
            if not existing_alert:
                await self.create_alert(
                    alert_type="sla_breach",
                    severity="critical",
                    title=f"CRITICAL: SLA Breach - Complaint #{complaint.id}",
                    message=f"Complaint #{complaint.id} has breached SLA deadline. Immediate action required.",
                    resource_type="complaint",
                    resource_id=complaint.id,
                    assigned_to_staff_id=complaint.assigned_to_staff_id,
                    metadata={"priority": complaint.priority.value if complaint.priority else None},
                    expires_in_hours=48
                )
                alerts_created += 1
        
        logger.info(f"SLA check complete: {alerts_created} alerts created")
        return alerts_created
    
    async def check_critical_complaints(self) -> int:
        """
        Check for new critical complaints
        Creates alerts for critical priority complaints
        
        Returns:
            Number of alerts created
        """
        from sqlalchemy import select, and_
        
        # Get critical complaints created in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        query = select(Complaint).where(
            and_(
                Complaint.priority == ComplaintPriority.CRITICAL,
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS]),
                Complaint.created_at >= one_hour_ago
            )
        )
        
        result = await self.db.execute(query)
        critical_complaints = result.scalars().all()
        
        alerts_created = 0
        
        for complaint in critical_complaints:
            existing_alert = await self._check_existing_alert(
                alert_type="critical_complaint",
                resource_type="complaint",
                resource_id=complaint.id
            )
            
            if not existing_alert:
                await self.create_alert(
                    alert_type="critical_complaint",
                    severity="critical",
                    title=f"CRITICAL Complaint: #{complaint.id}",
                    message=f"A new CRITICAL priority complaint has been created. Immediate attention required.",
                    resource_type="complaint",
                    resource_id=complaint.id,
                    assigned_to_staff_id=complaint.assigned_to_staff_id,
                    metadata={"complaint_type": complaint.complaint_type.value if complaint.complaint_type else None},
                    expires_in_hours=24
                )
                alerts_created += 1
        
        logger.info(f"Critical complaint check complete: {alerts_created} alerts created")
        return alerts_created
    
    async def _check_existing_alert(
        self,
        alert_type: str,
        resource_type: str,
        resource_id: int
    ) -> bool:
        """Check if alert already exists for resource"""
        from sqlalchemy import select, and_
        
        # Check for non-dismissed alerts created in last 24 hours
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        
        query = select(Alert).where(
            and_(
                Alert.alert_type == alert_type,
                Alert.resource_type == resource_type,
                Alert.resource_id == resource_id,
                Alert.is_dismissed == False,
                Alert.created_at >= one_day_ago
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def cleanup_old_alerts(self, days: int = 30) -> int:
        """Delete old dismissed or expired alerts"""
        deleted = await self.alert_repo.delete_expired_alerts()
        await self.db.commit()
        
        logger.info(f"Cleanup complete: {deleted} expired alerts deleted")
        return deleted

