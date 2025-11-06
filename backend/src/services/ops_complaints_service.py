"""
Operations Complaints Service
Business logic for complaint management operations
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import joinedload, selectinload

from src.core.models import (
    Complaint, ComplaintUpdate, Staff, User, Booking, Role,
    ComplaintType, ComplaintPriority, ComplaintStatus
)
from src.services.audit_service import AuditService
from src.schemas.ops_complaints import (
    ComplaintListRequest, ComplaintResponse, ComplaintListResponse,
    ComplaintUpdateRequest, ComplaintAssignRequest, ComplaintResolveRequest,
    ComplaintNoteRequest, UserInfo, BookingInfo, StaffInfo, ComplaintUpdateInfo
)

logger = logging.getLogger(__name__)


class OpsComplaintsService:
    """
    Service for operations complaint management
    
    Handles complaint CRUD operations, assignment workflow,
    resolution management, and audit logging
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
        self.logger = logger
    
    async def list_complaints(
        self,
        current_staff: Staff,
        filters: ComplaintListRequest,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintListResponse:
        """
        List complaints with filtering, sorting, and pagination
        
        Args:
            current_staff: Current staff member
            filters: Filter and pagination parameters
            request_metadata: Request metadata for audit
            
        Returns:
            Paginated list of complaints
        """
        try:
            # Check PII access permission
            has_full_access = await self._check_full_access_permission(current_staff)
            
            # Build query with eager loading
            query = select(Complaint).options(
                joinedload(Complaint.user),
                joinedload(Complaint.booking),
                joinedload(Complaint.assigned_to_staff),
                joinedload(Complaint.resolved_by_staff),
                selectinload(Complaint.updates)
            )
            
            # Apply filters
            query = self._apply_filters(query, filters)
            
            # Get total count
            count_query = select(func.count(Complaint.id))
            count_query = self._apply_filters(count_query, filters)
            total_result = await self.db.execute(count_query)
            total = total_result.scalar() or 0
            
            # Apply sorting
            query = self._apply_sorting(query, filters.sort_by, filters.sort_order)
            
            # Apply pagination
            query = query.offset(filters.skip).limit(filters.limit)
            
            # Execute query
            result = await self.db.execute(query)
            complaints = result.scalars().unique().all()
            
            # Convert to response format
            complaint_responses = []
            for complaint in complaints:
                complaint_response = await self._build_complaint_response(
                    complaint, has_full_access
                )
                complaint_responses.append(complaint_response)
            
            # Audit log
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="list_complaints",
                resource_type="complaint",
                resource_id=None,
                pii_accessed=has_full_access,
                metadata={
                    "filters": filters.dict(),
                    "result_count": len(complaints),
                    "has_full_access": has_full_access
                },
                request_metadata=request_metadata
            )
            
            self.logger.info(
                f"Listed {len(complaints)} complaints for staff {current_staff.id} "
                f"(total={total}, filters={filters.dict()})"
            )
            
            return ComplaintListResponse(
                complaints=complaint_responses,
                total=total,
                skip=filters.skip,
                limit=filters.limit,
                has_more=(filters.skip + len(complaints)) < total
            )
            
        except Exception as e:
            self.logger.error(f"Error listing complaints: {e}", exc_info=True)
            raise
    
    async def get_complaint_by_id(
        self,
        complaint_id: int,
        current_staff: Staff,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintResponse:
        """
        Get complaint by ID with full details
        
        Args:
            complaint_id: Complaint ID
            current_staff: Current staff member
            request_metadata: Request metadata for audit
            
        Returns:
            Full complaint details
        """
        try:
            # Check PII access permission
            has_full_access = await self._check_full_access_permission(current_staff)
            
            # Query complaint with relationships
            query = select(Complaint).options(
                joinedload(Complaint.user),
                joinedload(Complaint.booking),
                joinedload(Complaint.assigned_to_staff),
                joinedload(Complaint.resolved_by_staff),
                selectinload(Complaint.updates).joinedload(ComplaintUpdate.staff)
            ).where(Complaint.id == complaint_id)
            
            result = await self.db.execute(query)
            complaint = result.scalar_one_or_none()
            
            if not complaint:
                raise ValueError(f"Complaint {complaint_id} not found")
            
            # Build response
            complaint_response = await self._build_complaint_response(
                complaint, has_full_access, include_updates=True
            )
            
            # Audit log
            await self.audit_service.log_complaint_access(
                staff_id=current_staff.id,
                complaint_id=complaint_id,
                action="view_complaint",
                pii_accessed=has_full_access,
                request_metadata=request_metadata
            )
            
            self.logger.info(f"Retrieved complaint {complaint_id} for staff {current_staff.id}")
            
            return complaint_response
            
        except Exception as e:
            self.logger.error(f"Error getting complaint {complaint_id}: {e}", exc_info=True)
            raise
    
    async def update_complaint(
        self,
        complaint_id: int,
        update_data: ComplaintUpdateRequest,
        current_staff: Staff,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintResponse:
        """
        Update complaint fields
        
        Args:
            complaint_id: Complaint ID
            update_data: Fields to update
            current_staff: Current staff member
            request_metadata: Request metadata for audit
            
        Returns:
            Updated complaint details
        """
        try:
            # Get complaint
            complaint = await self._get_complaint_or_raise(complaint_id)
            
            # Track changes for audit
            changes = {}
            
            # Update fields
            if update_data.status:
                old_status = complaint.status.value if complaint.status else None
                complaint.status = ComplaintStatus(update_data.status)
                changes['status'] = {'old': old_status, 'new': update_data.status}
                
                # Set resolved timestamp if resolving
                if update_data.status in ['resolved', 'closed'] and not complaint.resolved_at:
                    complaint.resolved_at = datetime.now(timezone.utc)
                    complaint.resolved_by_staff_id = current_staff.id
            
            if update_data.priority:
                old_priority = complaint.priority.value if complaint.priority else None
                complaint.priority = ComplaintPriority(update_data.priority)
                changes['priority'] = {'old': old_priority, 'new': update_data.priority}
            
            if update_data.resolution:
                old_resolution = complaint.resolution
                complaint.resolution = update_data.resolution
                changes['resolution'] = {'old': old_resolution, 'new': update_data.resolution}
            
            # Save changes
            await self.db.commit()
            await self.db.refresh(complaint)
            
            # Build response
            has_full_access = await self._check_full_access_permission(current_staff)
            complaint_response = await self._build_complaint_response(complaint, has_full_access)
            
            # Audit log (don't auto-commit, let transaction handle it)
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="update_complaint",
                resource_type="complaint",
                resource_id=complaint_id,
                pii_accessed=False,
                metadata={"changes": changes},
                request_metadata=request_metadata,
                auto_commit=False
            )
            
            self.logger.info(
                f"Updated complaint {complaint_id} by staff {current_staff.id}: {changes}"
            )
            
            return complaint_response
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error updating complaint {complaint_id}: {e}", exc_info=True)
            raise
    
    async def assign_complaint(
        self,
        complaint_id: int,
        assign_data: ComplaintAssignRequest,
        current_staff: Staff,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintResponse:
        """
        Assign complaint to staff member
        
        Args:
            complaint_id: Complaint ID
            assign_data: Assignment data
            current_staff: Current staff member
            request_metadata: Request metadata for audit
            
        Returns:
            Updated complaint details
        """
        try:
            # Get complaint and target staff
            complaint = await self._get_complaint_or_raise(complaint_id)
            target_staff = await self._get_staff_or_raise(assign_data.assigned_to_staff_id)
            
            # Track changes
            old_assigned_to = complaint.assigned_to_staff_id
            
            # Update assignment
            complaint.assigned_to_staff_id = assign_data.assigned_to_staff_id
            complaint.assigned_at = datetime.now(timezone.utc)
            
            # Update status to in_progress if currently open
            if complaint.status == ComplaintStatus.OPEN:
                complaint.status = ComplaintStatus.IN_PROGRESS
            
            # Add assignment note if provided
            if assign_data.notes:
                assignment_note = ComplaintUpdate(
                    complaint_id=complaint_id,
                    user_id=complaint.user_id,
                    staff_id=current_staff.id,
                    comment=f"Assigned to {target_staff.first_name} {target_staff.last_name or ''}. {assign_data.notes}",
                    is_internal=True
                )
                self.db.add(assignment_note)
            
            # Save changes
            await self.db.commit()
            await self.db.refresh(complaint)
            
            # Build response
            has_full_access = await self._check_full_access_permission(current_staff)
            complaint_response = await self._build_complaint_response(complaint, has_full_access)
            
            # Audit log (don't auto-commit, let transaction handle it)
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="assign_complaint",
                resource_type="complaint",
                resource_id=complaint_id,
                pii_accessed=False,
                metadata={
                    "changes": {
                        'assigned_to_staff_id': {
                            'old': old_assigned_to,
                            'new': assign_data.assigned_to_staff_id
                        }
                    },
                    "target_staff_id": assign_data.assigned_to_staff_id
                },
                request_metadata=request_metadata,
                auto_commit=False
            )
            
            self.logger.info(
                f"Assigned complaint {complaint_id} to staff {assign_data.assigned_to_staff_id} "
                f"by staff {current_staff.id}"
            )
            
            return complaint_response
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error assigning complaint {complaint_id}: {e}", exc_info=True)
            raise

    async def resolve_complaint(
        self,
        complaint_id: int,
        resolve_data: ComplaintResolveRequest,
        current_staff: Staff,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintResponse:
        """
        Resolve complaint with resolution text

        Args:
            complaint_id: Complaint ID
            resolve_data: Resolution data
            current_staff: Current staff member
            request_metadata: Request metadata for audit

        Returns:
            Resolved complaint details
        """
        try:
            # Get complaint
            complaint = await self._get_complaint_or_raise(complaint_id)

            # Track changes
            old_status = complaint.status.value if complaint.status else None
            old_resolution = complaint.resolution

            # Update resolution
            complaint.resolution = resolve_data.resolution
            complaint.status = ComplaintStatus(resolve_data.status)
            complaint.resolved_at = datetime.now(timezone.utc)
            complaint.resolved_by_staff_id = current_staff.id

            # Add resolution note
            resolution_note = ComplaintUpdate(
                complaint_id=complaint_id,
                user_id=complaint.user_id,
                staff_id=current_staff.id,
                comment=f"Complaint {resolve_data.status}. Resolution: {resolve_data.resolution}",
                is_internal=False  # Customer can see resolution
            )
            self.db.add(resolution_note)

            # Save changes
            await self.db.commit()
            await self.db.refresh(complaint)

            # Build response
            has_full_access = await self._check_full_access_permission(current_staff)
            complaint_response = await self._build_complaint_response(complaint, has_full_access)

            # Audit log (don't auto-commit, let transaction handle it)
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="resolve_complaint",
                resource_type="complaint",
                resource_id=complaint_id,
                pii_accessed=False,
                metadata={
                    "changes": {
                        'status': {'old': old_status, 'new': resolve_data.status},
                        'resolution': {'old': old_resolution, 'new': resolve_data.resolution}
                    }
                },
                request_metadata=request_metadata,
                auto_commit=False
            )

            self.logger.info(
                f"Resolved complaint {complaint_id} by staff {current_staff.id} "
                f"with status {resolve_data.status}"
            )

            return complaint_response

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error resolving complaint {complaint_id}: {e}", exc_info=True)
            raise

    async def add_complaint_update(
        self,
        complaint_id: int,
        note_data: ComplaintNoteRequest,
        current_staff: Staff,
        request_metadata: Optional[Dict] = None
    ) -> ComplaintUpdateInfo:
        """
        Add update/note to complaint

        Args:
            complaint_id: Complaint ID
            note_data: Note data
            current_staff: Current staff member
            request_metadata: Request metadata for audit

        Returns:
            Created complaint update
        """
        try:
            # Get complaint to verify it exists
            complaint = await self._get_complaint_or_raise(complaint_id)

            # Create update
            complaint_update = ComplaintUpdate(
                complaint_id=complaint_id,
                user_id=complaint.user_id,
                staff_id=current_staff.id,
                comment=note_data.comment,
                is_internal=note_data.is_internal
            )

            self.db.add(complaint_update)
            await self.db.commit()
            await self.db.refresh(complaint_update)

            # Build response
            staff_info = StaffInfo(
                id=current_staff.id,
                employee_id=current_staff.employee_id,
                name=f"{current_staff.first_name} {current_staff.last_name or ''}".strip(),
                department=current_staff.department
            )

            update_response = ComplaintUpdateInfo(
                id=complaint_update.id,
                comment=complaint_update.comment,
                is_internal=complaint_update.is_internal,
                staff_info=staff_info,
                created_at=complaint_update.created_at
            )

            # Audit log
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="add_complaint_update",
                resource_type="complaint",
                resource_id=complaint_id,
                pii_accessed=False,
                metadata={
                    'comment_length': len(note_data.comment),
                    'is_internal': note_data.is_internal
                },
                request_metadata=request_metadata
            )

            self.logger.info(
                f"Added update to complaint {complaint_id} by staff {current_staff.id} "
                f"(internal={note_data.is_internal})"
            )

            return update_response

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error adding update to complaint {complaint_id}: {e}", exc_info=True)
            raise

    async def get_complaint_updates(
        self,
        complaint_id: int,
        current_staff: Staff,
        include_internal: bool = True,
        request_metadata: Optional[Dict] = None
    ) -> List[ComplaintUpdateInfo]:
        """
        Get complaint updates/notes

        Args:
            complaint_id: Complaint ID
            current_staff: Current staff member
            include_internal: Whether to include internal notes
            request_metadata: Request metadata for audit

        Returns:
            List of complaint updates
        """
        try:
            # Verify complaint exists
            await self._get_complaint_or_raise(complaint_id)

            # Query updates
            query = select(ComplaintUpdate).options(
                joinedload(ComplaintUpdate.staff)
            ).where(ComplaintUpdate.complaint_id == complaint_id)

            # Filter internal notes if needed
            if not include_internal:
                query = query.where(ComplaintUpdate.is_internal == False)

            query = query.order_by(ComplaintUpdate.created_at.desc())

            result = await self.db.execute(query)
            updates = result.scalars().all()

            # Build response
            update_responses = []
            for update in updates:
                staff_info = None
                if update.staff:
                    staff_info = StaffInfo(
                        id=update.staff.id,
                        employee_id=update.staff.employee_id,
                        name=f"{update.staff.first_name} {update.staff.last_name or ''}".strip(),
                        department=update.staff.department
                    )

                update_response = ComplaintUpdateInfo(
                    id=update.id,
                    comment=update.comment,
                    is_internal=update.is_internal,
                    staff_info=staff_info,
                    created_at=update.created_at
                )
                update_responses.append(update_response)

            # Audit log (auto-commit for read operation)
            await self.audit_service.log_access(
                staff_id=current_staff.id,
                action="view_complaint_updates",
                resource_type="complaint",
                resource_id=complaint_id,
                pii_accessed=False,
                metadata={
                    "result_count": len(updates),
                    "include_internal": include_internal
                },
                request_metadata=request_metadata,
                auto_commit=True
            )

            self.logger.info(
                f"Retrieved {len(updates)} updates for complaint {complaint_id} "
                f"by staff {current_staff.id}"
            )

            return update_responses

        except Exception as e:
            self.logger.error(f"Error getting updates for complaint {complaint_id}: {e}", exc_info=True)
            raise

    # Helper Methods

    async def _check_full_access_permission(self, staff: Staff) -> bool:
        """Check if staff has full PII access permission"""
        # Always reload staff with role and permissions to avoid lazy loading issues
        from sqlalchemy.orm import selectinload
        from src.core.models.role import Role

        result = await self.db.execute(
            select(Staff)
            .options(selectinload(Staff.role).selectinload(Role.permissions))
            .where(Staff.id == staff.id)
        )
        staff_with_role = result.scalar_one()

        return staff_with_role.has_any_permission(["ops.priority_queue.full_access", "system.admin"])

    async def _get_complaint_or_raise(self, complaint_id: int) -> Complaint:
        """Get complaint by ID or raise ValueError if not found"""
        from sqlalchemy.orm import joinedload, selectinload

        result = await self.db.execute(
            select(Complaint)
            .options(
                joinedload(Complaint.user),
                joinedload(Complaint.booking),
                joinedload(Complaint.assigned_to_staff),
                joinedload(Complaint.resolved_by_staff),
                selectinload(Complaint.updates)
            )
            .where(Complaint.id == complaint_id)
        )
        complaint = result.scalar_one_or_none()
        if not complaint:
            raise ValueError(f"Complaint {complaint_id} not found")
        return complaint

    async def _get_staff_or_raise(self, staff_id: int) -> Staff:
        """Get staff by ID or raise ValueError if not found"""
        result = await self.db.execute(
            select(Staff).where(Staff.id == staff_id)
        )
        staff = result.scalar_one_or_none()
        if not staff:
            raise ValueError(f"Staff {staff_id} not found")
        return staff

    def _apply_filters(self, query, filters: ComplaintListRequest):
        """Apply filters to complaint query"""

        # Status filter
        if filters.status and filters.status != 'all':
            try:
                status_enum = ComplaintStatus(filters.status)
                query = query.where(Complaint.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter

        # Priority filter
        if filters.priority and filters.priority != 'all':
            try:
                priority_enum = ComplaintPriority(filters.priority)
                query = query.where(Complaint.priority == priority_enum)
            except ValueError:
                pass  # Invalid priority, ignore filter

        # Complaint type filter
        if filters.complaint_type:
            try:
                type_enum = ComplaintType(filters.complaint_type)
                query = query.where(Complaint.complaint_type == type_enum)
            except ValueError:
                pass  # Invalid type, ignore filter

        # Assigned to filter
        if filters.assigned_to:
            query = query.where(Complaint.assigned_to_staff_id == filters.assigned_to)

        # Date range filters
        if filters.date_from:
            query = query.where(Complaint.created_at >= filters.date_from)
        if filters.date_to:
            query = query.where(Complaint.created_at <= filters.date_to)

        # SLA risk filter
        if filters.sla_risk is not None:
            now = datetime.now(timezone.utc)
            if filters.sla_risk:
                # At risk: response overdue OR resolution due within 25% of total time
                query = query.where(
                    or_(
                        and_(
                            Complaint.response_due_at.isnot(None),
                            Complaint.response_due_at <= now
                        ),
                        and_(
                            Complaint.resolution_due_at.isnot(None),
                            Complaint.resolution_due_at <= now + timedelta(hours=6)  # Simplified risk calculation
                        )
                    )
                )
            else:
                # Not at risk
                query = query.where(
                    and_(
                        or_(
                            Complaint.response_due_at.is_(None),
                            Complaint.response_due_at > now
                        ),
                        or_(
                            Complaint.resolution_due_at.is_(None),
                            Complaint.resolution_due_at > now + timedelta(hours=6)
                        )
                    )
                )

        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """Apply sorting to complaint query"""

        # Map sort fields
        sort_field_map = {
            'created_at': Complaint.created_at,
            'priority': Complaint.priority,
            'status': Complaint.status,
            'response_due_at': Complaint.response_due_at,
            'resolution_due_at': Complaint.resolution_due_at
        }

        sort_field = sort_field_map.get(sort_by, Complaint.created_at)

        if sort_order == 'asc':
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))

        return query

    async def _build_complaint_response(
        self,
        complaint: Complaint,
        has_full_access: bool,
        include_updates: bool = False
    ) -> ComplaintResponse:
        """Build complaint response with proper PII handling"""

        # User info with PII redaction
        user_info = UserInfo(
            id=complaint.user.id,
            name=complaint.user.first_name if has_full_access else "***",
            email=complaint.user.email if has_full_access else "***@***.com",
            mobile=complaint.user.mobile if has_full_access else "***-***-****"
        )

        # Booking info if available
        booking_info = None
        if complaint.booking:
            booking_info = BookingInfo(
                id=complaint.booking.id,
                order_id=complaint.booking.order_id,
                status=complaint.booking.status.value,
                total_amount=float(complaint.booking.total) if complaint.booking.total else None,
                scheduled_date=complaint.booking.preferred_date
            )

        # Assigned staff info
        assigned_to_staff = None
        if complaint.assigned_to_staff:
            assigned_to_staff = StaffInfo(
                id=complaint.assigned_to_staff.id,
                employee_id=complaint.assigned_to_staff.employee_id,
                name=f"{complaint.assigned_to_staff.first_name} {complaint.assigned_to_staff.last_name or ''}".strip(),
                department=complaint.assigned_to_staff.department
            )

        # Resolved by staff info
        resolved_by_staff = None
        if complaint.resolved_by_staff:
            resolved_by_staff = StaffInfo(
                id=complaint.resolved_by_staff.id,
                employee_id=complaint.resolved_by_staff.employee_id,
                name=f"{complaint.resolved_by_staff.first_name} {complaint.resolved_by_staff.last_name or ''}".strip(),
                department=complaint.resolved_by_staff.department
            )

        # Calculate SLA breach risk
        sla_breach_risk = self._calculate_sla_risk(complaint)

        # Updates count
        updates_count = len(complaint.updates) if complaint.updates else 0

        return ComplaintResponse(
            id=complaint.id,
            complaint_type=complaint.complaint_type.value,
            subject=complaint.subject,
            description=complaint.description,
            status=complaint.status.value,
            priority=complaint.priority.value,
            user_info=user_info,
            booking_info=booking_info,
            assigned_to_staff=assigned_to_staff,
            resolved_by_staff=resolved_by_staff,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
            assigned_at=complaint.assigned_at,
            resolved_at=complaint.resolved_at,
            response_due_at=complaint.response_due_at,
            resolution_due_at=complaint.resolution_due_at,
            sla_breach_risk=sla_breach_risk,
            resolution=complaint.resolution,
            updates_count=updates_count
        )

    def _calculate_sla_risk(self, complaint: Complaint) -> bool:
        """Calculate if complaint is at risk of SLA breach"""
        now = datetime.now(timezone.utc)

        # Response overdue
        if complaint.response_due_at:
            # Make response_due_at timezone-aware if it's naive
            response_due = complaint.response_due_at
            if response_due.tzinfo is None:
                response_due = response_due.replace(tzinfo=timezone.utc)
            if now >= response_due:
                return True

        # Resolution at risk (within 25% of deadline)
        if complaint.resolution_due_at:
            # Make resolution_due_at timezone-aware if it's naive
            resolution_due = complaint.resolution_due_at
            if resolution_due.tzinfo is None:
                resolution_due = resolution_due.replace(tzinfo=timezone.utc)

            time_remaining = resolution_due - now
            if time_remaining.total_seconds() <= 0:
                return True

            # Calculate if within 25% of total time
            created_at = complaint.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            total_time = resolution_due - created_at
            risk_threshold = total_time.total_seconds() * 0.25

            if time_remaining.total_seconds() <= risk_threshold:
                return True

        return False
