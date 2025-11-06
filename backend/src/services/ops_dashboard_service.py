"""
Ops Dashboard Service - Business logic for ops dashboard operations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.models import (
    PriorityQueue, User, Staff, Complaint, Booking, 
    ComplaintPriority, ComplaintStatus, BookingStatus
)
from src.repositories.priority_queue_repository import PriorityQueueRepository
from src.services.config_service import ConfigService
from src.services.audit_service import AuditService
from src.schemas.ops_dashboard import PriorityQueueFilters


class OpsDashboardService:
    """
    Service for ops dashboard operations
    
    Handles business logic for:
    - Priority queue retrieval with filtering
    - PII redaction based on permissions
    - Related entity enrichment
    - SLA breach risk calculation
    - Audit logging
    - Metrics tracking
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ops dashboard service
        
        Args:
            db: Async database session
        """
        self.db = db
        self.priority_queue_repo = PriorityQueueRepository(db)
        self.config_service = ConfigService(db)
        self.audit_service = AuditService(db)
        self.logger = logging.getLogger(__name__)
    
    async def get_priority_queue(
        self,
        current_staff: Staff,
        status: Optional[str] = None,
        intent_type: Optional[str] = None,
        priority_min: Optional[int] = None,
        priority_max: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "priority_score",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20,
        expand: bool = False,
        fields: Optional[str] = None,
        request_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get priority queue items with filtering and pagination
        
        Args:
            current_staff: Current staff user (for permission checks)
            status: Filter by review status ('pending', 'reviewed', 'all')
            intent_type: Filter by intent type
            priority_min: Minimum priority score
            priority_max: Maximum priority score
            date_from: Filter from date
            date_to: Filter to date
            sort_by: Field to sort by
            sort_order: Sort order (asc, desc)
            skip: Pagination offset
            limit: Pagination limit
            expand: Fetch full related entity details
            fields: Specific fields to include in expansion
            request_metadata: Request metadata for audit logging
        
        Returns:
            Dict with items, total count, pagination info
        """
        try:
            # 1. Apply default filters based on configuration
            if status is None:
                status = await self.config_service.get_config(
                    "DEFAULT_STATUS_FILTER",
                    default="pending"
                )
            
            # 2. Check permissions for PII access
            has_full_access = await self._check_full_access_permission(current_staff)
            
            # 3. Build filters
            filters = self._build_filters(
                status, intent_type, priority_min, priority_max,
                date_from, date_to
            )
            
            # 4. Query repository (only paginated results)
            items = await self.priority_queue_repo.get_priority_items(
                filters, sort_by, sort_order, skip, limit
            )
            total = await self.priority_queue_repo.count_priority_items(filters)
            
            # 5. Enrich ONLY paginated results
            enriched_items = []
            for item in items:
                enriched = await self._enrich_priority_item(
                    item,
                    expand=expand,
                    fields=fields,
                    has_full_access=has_full_access
                )
                enriched_items.append(enriched)
            
            # 6. Audit logging
            await self.audit_service.log_priority_queue_access(
                staff_id=current_staff.id,
                has_full_access=has_full_access,
                expand=expand,
                filters=filters,
                result_count=len(items),
                request_metadata=request_metadata
            )
            
            # 7. Track metrics (placeholder for future implementation)
            await self._track_metrics(
                action="get_priority_queue",
                expand=expand,
                result_count=len(items)
            )
            
            self.logger.info(
                f"Retrieved {len(items)} priority queue items for staff {current_staff.id} "
                f"(total={total}, expand={expand}, has_full_access={has_full_access})"
            )
            
            return {
                "items": enriched_items,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
            
        except Exception as e:
            self.logger.error(
                f"Error retrieving priority queue for staff {current_staff.id}: {e}",
                exc_info=True
            )
            raise
    
    async def _check_full_access_permission(self, staff: Staff) -> bool:
        """
        Check if staff has ops.priority_queue.full_access permission for PII
        
        Args:
            staff: Staff instance
        
        Returns:
            True if staff has full access permission
        """
        try:
            # Get staff permissions from role
            if not staff.role:
                return False
            
            # Check if role has ops.priority_queue.full_access or system.admin permission
            permissions = await self._get_staff_permissions(staff)

            has_access = (
                "ops.priority_queue.full_access" in permissions or
                "system.admin" in permissions
            )
            
            self.logger.debug(
                f"Staff {staff.id} full access check: {has_access} "
                f"(permissions: {permissions})"
            )
            
            return has_access
            
        except Exception as e:
            self.logger.error(
                f"Error checking full access permission for staff {staff.id}: {e}",
                exc_info=True
            )
            # Default to False for security
            return False
    
    async def _get_staff_permissions(self, staff: Staff) -> List[str]:
        """
        Get list of permission names for staff
        
        Args:
            staff: Staff instance
        
        Returns:
            List of permission names
        """
        try:
            if not staff.role:
                return []
            
            # Get permissions from role
            result = await self.db.execute(
                select(Staff).where(Staff.id == staff.id)
            )
            staff_with_role = result.scalar_one_or_none()
            
            if not staff_with_role or not staff_with_role.role:
                return []
            
            # Extract permission names from role
            permissions = []
            if hasattr(staff_with_role.role, 'permissions'):
                for perm in staff_with_role.role.permissions:
                    if hasattr(perm, 'name'):
                        permissions.append(perm.name)
            
            return permissions
            
        except Exception as e:
            self.logger.error(
                f"Error getting staff permissions for staff {staff.id}: {e}",
                exc_info=True
            )
            return []
    
    def _build_filters(
        self,
        status: Optional[str],
        intent_type: Optional[str],
        priority_min: Optional[int],
        priority_max: Optional[int],
        date_from: Optional[datetime],
        date_to: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Build filters dictionary for repository
        
        Args:
            status: Review status filter
            intent_type: Intent type filter
            priority_min: Minimum priority score
            priority_max: Maximum priority score
            date_from: From date
            date_to: To date
        
        Returns:
            Dictionary of filters
        """
        filters = {}
        
        if status:
            filters["status"] = status
        
        if intent_type:
            filters["intent_type"] = intent_type
        
        if priority_min is not None:
            filters["priority_min"] = priority_min
        
        if priority_max is not None:
            filters["priority_max"] = priority_max
        
        if date_from:
            filters["date_from"] = date_from
        
        if date_to:
            filters["date_to"] = date_to
        
        return filters
    
    async def _track_metrics(
        self,
        action: str,
        expand: bool,
        result_count: int
    ):
        """
        Track metrics for monitoring

        Placeholder for future metrics implementation.
        Could integrate with Prometheus, CloudWatch, etc.

        Args:
            action: Action performed
            expand: Whether expand was used
            result_count: Number of results returned
        """
        # TODO: Implement metrics tracking
        # - Page latency
        # - Enrichment latency
        # - Expand usage rate
        # - Result count distribution
        pass

    async def _enrich_priority_item(
        self,
        item: PriorityQueue,
        expand: bool = False,
        fields: Optional[str] = None,
        has_full_access: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich priority queue item with related entity data

        Args:
            item: PriorityQueue model instance
            expand: Fetch full details
            fields: Specific fields to include
            has_full_access: Whether staff has PII access

        Returns:
            Enriched dictionary with related entity info
        """
        try:
            # Base item data
            item_dict = item.to_dict()

            # Add user details (with PII control)
            user = await self._get_user_details(item.user_id, has_full_access)
            item_dict.update({
                "user_name": user.get("name"),
                "user_mobile": user.get("mobile"),
                "user_email": user.get("email")
            })

            # Add reviewer details if reviewed
            if item.reviewed_by_staff_id and item.reviewed_by_staff:
                item_dict["reviewed_by_staff_name"] = (
                    f"{item.reviewed_by_staff.first_name} "
                    f"{item.reviewed_by_staff.last_name or ''}".strip()
                )

            # Redact PII if no full access
            if not has_full_access:
                item_dict = self._redact_pii(item_dict)

            # Add related entity (summary or full)
            if expand:
                # Full details - more expensive
                related_entity = await self._get_full_related_entity(
                    item.intent_type.value,
                    item.session_id,
                    fields
                )
            else:
                # Summary only - fast
                related_entity = await self._get_summary_related_entity(
                    item.intent_type.value,
                    item.session_id
                )

            item_dict["related_entity"] = related_entity

            return item_dict

        except Exception as e:
            self.logger.error(
                f"Error enriching priority item {item.id}: {e}",
                exc_info=True
            )
            # Return basic item data without enrichment
            return item.to_dict()

    async def _get_user_details(
        self,
        user_id: int,
        has_full_access: bool
    ) -> Dict[str, Optional[str]]:
        """
        Get user details with PII control

        Args:
            user_id: User ID
            has_full_access: Whether to include full PII

        Returns:
            Dictionary with user details
        """
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {"name": None, "mobile": None, "email": None}

            return {
                "name": f"{user.first_name} {user.last_name or ''}".strip(),
                "mobile": user.mobile,
                "email": user.email
            }

        except Exception as e:
            self.logger.error(f"Error getting user details for user {user_id}: {e}")
            return {"name": None, "mobile": None, "email": None}

    def _redact_pii(self, item_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PII fields for users without full access

        Args:
            item_dict: Item dictionary

        Returns:
            Dictionary with redacted PII
        """
        # Redact mobile: 9876543210 -> 98****3210
        if item_dict.get("user_mobile"):
            mobile = item_dict["user_mobile"]
            if len(mobile) >= 6:
                item_dict["user_mobile"] = f"{mobile[:2]}****{mobile[-4:]}"
            else:
                item_dict["user_mobile"] = "****"

        # Redact email: john@example.com -> j***@example.com
        if item_dict.get("user_email"):
            email = item_dict["user_email"]
            parts = email.split("@")
            if len(parts) == 2 and len(parts[0]) > 0:
                item_dict["user_email"] = f"{parts[0][0]}***@{parts[1]}"
            else:
                item_dict["user_email"] = "***@***"

        # Redact name: John Doe -> John D.
        if item_dict.get("user_name"):
            name_parts = item_dict["user_name"].split()
            if len(name_parts) > 1:
                item_dict["user_name"] = f"{name_parts[0]} {name_parts[-1][0]}."

        # Truncate message snippet
        if item_dict.get("message_snippet"):
            snippet = item_dict["message_snippet"]
            if len(snippet) > 100:
                item_dict["message_snippet"] = snippet[:100] + "..."

        return item_dict

    async def _get_summary_related_entity(
        self,
        intent_type: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get summary of related entity (fast)

        Args:
            intent_type: Intent type (complaint, booking, etc.)
            session_id: Session ID

        Returns:
            Summary dictionary or None
        """
        try:
            if intent_type == "complaint":
                complaint = await self._get_complaint_by_session(session_id)
                if complaint:
                    return {
                        "type": "complaint",
                        "id": complaint.id,
                        "status": complaint.status.value,
                        "priority": complaint.priority.value,
                        "sla_breach_risk": self._calculate_sla_risk(complaint),
                        "response_due_at": complaint.response_due_at.isoformat() if complaint.response_due_at else None
                    }

            elif intent_type == "booking":
                booking = await self._get_booking_by_session(session_id)
                if booking:
                    return {
                        "type": "booking",
                        "id": booking.id,
                        "status": booking.status.value,
                        "priority": self._calculate_booking_priority(booking),
                        "sla_breach_risk": False,  # Bookings don't have SLA
                        "response_due_at": None
                    }

            # Add more intent types as needed (refund, cancellation, etc.)

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting summary for intent_type={intent_type}, "
                f"session_id={session_id}: {e}"
            )
            return None

    async def _get_full_related_entity(
        self,
        intent_type: str,
        session_id: str,
        fields: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get full details of related entity (expensive)

        Args:
            intent_type: Intent type
            session_id: Session ID
            fields: Specific fields to include

        Returns:
            Full details dictionary or None
        """
        try:
            # Parse fields parameter
            requested_fields = set(fields.split(",")) if fields else None

            if intent_type == "complaint":
                complaint = await self._get_complaint_by_session(session_id)
                if complaint:
                    details = {
                        "subject": complaint.subject,
                        "complaint_type": complaint.complaint_type.value,
                        "description": complaint.description,
                        "assigned_to_staff_id": complaint.assigned_to_staff_id,
                        "booking_id": complaint.booking_id
                    }

                    # Add assigned staff name if available
                    if complaint.assigned_to_staff:
                        details["assigned_to_staff_name"] = (
                            f"{complaint.assigned_to_staff.first_name} "
                            f"{complaint.assigned_to_staff.last_name or ''}".strip()
                        )

                    # Filter fields if requested
                    if requested_fields:
                        details = {
                            k: v for k, v in details.items()
                            if k in requested_fields
                        }

                    return {
                        "type": "complaint",
                        "id": complaint.id,
                        "status": complaint.status.value,
                        "priority": complaint.priority.value,
                        "sla_breach_risk": self._calculate_sla_risk(complaint),
                        "response_due_at": complaint.response_due_at.isoformat() if complaint.response_due_at else None,
                        "resolution_due_at": complaint.resolution_due_at.isoformat() if complaint.resolution_due_at else None,
                        "details": details
                    }

            elif intent_type == "booking":
                booking = await self._get_booking_by_session(session_id)
                if booking:
                    details = {
                        "booking_number": booking.booking_number,
                        "total": float(booking.total),
                        "payment_status": booking.payment_status.value,
                        "payment_method": booking.payment_method.value,
                        "preferred_date": booking.preferred_date.isoformat(),
                        "preferred_time": booking.preferred_time.isoformat()
                    }

                    # Filter fields if requested
                    if requested_fields:
                        details = {
                            k: v for k, v in details.items()
                            if k in requested_fields
                        }

                    return {
                        "type": "booking",
                        "id": booking.id,
                        "status": booking.status.value,
                        "priority": self._calculate_booking_priority(booking),
                        "sla_breach_risk": False,
                        "response_due_at": None,
                        "resolution_due_at": None,
                        "details": details
                    }

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting full details for intent_type={intent_type}, "
                f"session_id={session_id}: {e}",
                exc_info=True
            )
            return None

    async def _get_complaint_by_session(self, session_id: str) -> Optional[Complaint]:
        """Get complaint by session ID"""
        try:
            result = await self.db.execute(
                select(Complaint).where(Complaint.session_id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting complaint by session {session_id}: {e}")
            return None

    async def _get_booking_by_session(self, session_id: str) -> Optional[Booking]:
        """Get booking by session ID (via conversation)"""
        try:
            # Bookings don't have session_id directly
            # Need to find via conversation or other means
            # For now, return None - this needs proper implementation
            # based on how bookings are linked to sessions
            return None
        except Exception as e:
            self.logger.error(f"Error getting booking by session {session_id}: {e}")
            return None

    def _calculate_sla_risk(self, complaint: Complaint) -> bool:
        """
        Calculate if complaint is at risk of SLA breach

        Args:
            complaint: Complaint instance

        Returns:
            True if at risk of SLA breach
        """
        if not complaint.response_due_at:
            return False

        # Get buffer time from config (default 1 hour)
        # For now, use hardcoded 1 hour
        buffer_hours = 1

        now = datetime.now(timezone.utc)
        buffer_time = timedelta(hours=buffer_hours)

        # At risk if due time is within buffer window
        return complaint.response_due_at <= (now + buffer_time)

    def _calculate_booking_priority(self, booking: Booking) -> str:
        """
        Calculate priority for booking

        Args:
            booking: Booking instance

        Returns:
            Priority level (high, medium, low)
        """
        # Simple priority calculation based on status
        if booking.status == BookingStatus.PENDING:
            return "high"
        elif booking.status == BookingStatus.CONFIRMED:
            return "medium"
        else:
            return "low"

