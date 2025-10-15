"""
Audit Service for logging ops operations and PII access
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import OpsAuditLog


class AuditService:
    """
    Service for audit logging
    
    Tracks all operational access and actions for:
    - Compliance requirements
    - Security monitoring
    - PII access tracking
    - Incident investigation
    
    Critical for maintaining audit trail of who accessed what data and when.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize audit service
        
        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def log_access(
        self,
        staff_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        pii_accessed: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> OpsAuditLog:
        """
        Log ops access for audit trail
        
        Args:
            staff_id: ID of staff member performing action
            action: Action performed (e.g., 'view_priority_queue', 'expand_details')
            resource_type: Type of resource accessed (e.g., 'priority_queue', 'complaint')
            resource_id: ID of specific resource (optional)
            pii_accessed: Whether PII was accessed (critical for compliance)
            metadata: Additional metadata (filters, params, etc.)
            request_metadata: Request metadata (IP, user agent, etc.)
        
        Returns:
            Created OpsAuditLog instance
        """
        try:
            # Create audit log entry
            audit_log = OpsAuditLog(
                staff_id=staff_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                pii_accessed=pii_accessed,
                request_metadata=metadata,
                ip_address=request_metadata.get("ip") if request_metadata else None,
                user_agent=request_metadata.get("user_agent") if request_metadata else None
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            await self.db.refresh(audit_log)
            
            # Also log to application logs for immediate visibility
            log_message = (
                f"Audit: staff_id={staff_id} action={action} "
                f"resource={resource_type}"
            )
            
            if resource_id:
                log_message += f":{resource_id}"
            
            if pii_accessed:
                log_message += " [PII_ACCESSED]"
            
            # Use WARNING level for PII access to make it more visible
            if pii_accessed:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return audit_log
            
        except Exception as e:
            self.logger.error(
                f"Error creating audit log: staff_id={staff_id}, action={action}, "
                f"error={e}",
                exc_info=True
            )
            # Don't raise - audit logging failure shouldn't break the main operation
            # But log the error for investigation
            await self.db.rollback()
            raise
    
    async def log_priority_queue_access(
        self,
        staff_id: int,
        has_full_access: bool,
        expand: bool,
        filters: Dict[str, Any],
        result_count: int,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> OpsAuditLog:
        """
        Convenience method for logging priority queue access
        
        Args:
            staff_id: Staff ID
            has_full_access: Whether staff has ops.full_access permission
            expand: Whether full details were expanded
            filters: Filters applied to query
            result_count: Number of results returned
            request_metadata: Request metadata
        
        Returns:
            Created OpsAuditLog instance
        """
        action = "expand_priority_queue" if expand else "view_priority_queue"
        
        metadata = {
            "filters": filters,
            "expand": expand,
            "result_count": result_count,
            "has_full_access": has_full_access
        }
        
        return await self.log_access(
            staff_id=staff_id,
            action=action,
            resource_type="priority_queue",
            pii_accessed=has_full_access,  # PII accessed if has full access
            metadata=metadata,
            request_metadata=request_metadata
        )
    
    async def log_complaint_access(
        self,
        staff_id: int,
        complaint_id: int,
        action: str,
        pii_accessed: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> OpsAuditLog:
        """
        Convenience method for logging complaint access
        
        Args:
            staff_id: Staff ID
            complaint_id: Complaint ID
            action: Action performed
            pii_accessed: Whether PII was accessed
            request_metadata: Request metadata
        
        Returns:
            Created OpsAuditLog instance
        """
        return await self.log_access(
            staff_id=staff_id,
            action=action,
            resource_type="complaint",
            resource_id=complaint_id,
            pii_accessed=pii_accessed,
            request_metadata=request_metadata
        )
    
    async def log_booking_access(
        self,
        staff_id: int,
        booking_id: int,
        action: str,
        pii_accessed: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> OpsAuditLog:
        """
        Convenience method for logging booking access
        
        Args:
            staff_id: Staff ID
            booking_id: Booking ID
            action: Action performed
            pii_accessed: Whether PII was accessed
            request_metadata: Request metadata
        
        Returns:
            Created OpsAuditLog instance
        """
        return await self.log_access(
            staff_id=staff_id,
            action=action,
            resource_type="booking",
            resource_id=booking_id,
            pii_accessed=pii_accessed,
            request_metadata=request_metadata
        )

