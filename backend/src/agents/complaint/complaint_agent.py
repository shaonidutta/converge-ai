"""
ComplaintAgent - Handles customer complaints with AI-powered priority scoring

This agent manages the complete complaint workflow:
1. Creates complaint records with automatic priority scoring
2. Categorizes complaints by type
3. Calculates SLA deadlines
4. Provides tracking and status updates
5. Escalates critical issues
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.models import User, Complaint, ComplaintUpdate, Booking
from src.core.models.complaint import ComplaintType, ComplaintPriority, ComplaintStatus
from src.services.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class ComplaintAgent:
    """
    ComplaintAgent handles customer complaints with AI-powered priority scoring
    
    Features:
    - Automatic complaint type classification
    - AI-powered priority scoring (LOW/MEDIUM/HIGH/CRITICAL)
    - SLA deadline calculation
    - Complaint tracking and updates
    - Escalation for critical issues
    """
    
    # SLA deadlines (in hours) based on priority
    SLA_RESPONSE_TIME = {
        ComplaintPriority.CRITICAL: 1,   # 1 hour response
        ComplaintPriority.HIGH: 4,       # 4 hours response
        ComplaintPriority.MEDIUM: 24,    # 24 hours response
        ComplaintPriority.LOW: 48,       # 48 hours response
    }
    
    SLA_RESOLUTION_TIME = {
        ComplaintPriority.CRITICAL: 4,   # 4 hours resolution
        ComplaintPriority.HIGH: 24,      # 24 hours resolution
        ComplaintPriority.MEDIUM: 72,    # 72 hours resolution
        ComplaintPriority.LOW: 168,      # 168 hours (7 days) resolution
    }
    
    # Keywords for priority scoring
    CRITICAL_KEYWORDS = [
        "urgent", "emergency", "immediately", "asap", "critical", "severe",
        "dangerous", "unsafe", "injury", "damage", "fraud", "scam"
    ]
    
    HIGH_KEYWORDS = [
        "very bad", "terrible", "horrible", "worst", "unacceptable",
        "disappointed", "angry", "frustrated", "refund", "money back"
    ]
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ComplaintAgent

        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.response_generator = ResponseGenerator()
    
    async def execute(
        self,
        message: str,
        user: User,
        session_id: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complaint request
        
        Args:
            message: User message
            user: Current user
            session_id: Session ID
            entities: Extracted entities (complaint_type, description, booking_id, etc.)
        
        Returns:
            {
                "response": str,  # User-friendly message
                "action_taken": str,  # Action identifier
                "metadata": dict  # Complaint details
            }
        """
        try:
            action = entities.get("action", "create")
            
            if action == "create":
                return await self._create_complaint(message, user, session_id, entities)
            elif action == "status":
                return await self._get_complaint_status(user, entities)
            elif action == "update":
                return await self._add_complaint_update(user, entities)
            else:
                return {
                    "response": "I can help you file a complaint or check the status of an existing one. What would you like to do?",
                    "action_taken": "unknown_action",
                    "metadata": {"action": action}
                }
                
        except Exception as e:
            self.logger.error(f"Complaint agent error: {e}", exc_info=True)
            return {
                "response": "❌ An error occurred while processing your complaint. Please contact support directly.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _create_complaint(
        self,
        message: str,
        user: User,
        session_id: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new complaint
        
        Args:
            message: User message
            user: Current user
            session_id: Session ID
            entities: Extracted entities
        
        Returns:
            Response dict with complaint details
        """
        # Extract complaint details
        description = entities.get("description", message)
        subject = entities.get("subject", description[:100])  # First 100 chars as subject
        booking_id = entities.get("booking_id")
        complaint_type_str = entities.get("complaint_type", "other")
        
        # Validate description
        if not description or len(description) < 10:
            return {
                "response": "Please provide more details about your complaint. What exactly is the issue?",
                "action_taken": "missing_entity",
                "metadata": {"missing": "description"}
            }
        
        # Map complaint type
        complaint_type = self._map_complaint_type(complaint_type_str)
        
        # Calculate priority based on content
        priority = self._calculate_priority(description, complaint_type)
        
        # Validate booking if provided
        booking = None
        if booking_id:
            booking = await self._get_booking(int(booking_id), user)
            if not booking:
                return {
                    "response": f"❌ Booking #{booking_id} not found. Please check the booking number.",
                    "action_taken": "booking_not_found",
                    "metadata": {"booking_id": booking_id}
                }
        
        # Calculate SLA deadlines
        now = datetime.now(timezone.utc)
        response_due_at = now + timedelta(hours=self.SLA_RESPONSE_TIME[priority])
        resolution_due_at = now + timedelta(hours=self.SLA_RESOLUTION_TIME[priority])
        
        # Create complaint
        complaint = Complaint(
            user_id=user.id,
            booking_id=booking.id if booking else None,
            session_id=session_id,
            complaint_type=complaint_type,
            subject=subject,
            description=description,
            priority=priority,
            status=ComplaintStatus.OPEN,
            response_due_at=response_due_at,
            resolution_due_at=resolution_due_at
        )
        
        self.db.add(complaint)
        await self.db.commit()
        await self.db.refresh(complaint)
        
        self.logger.info(
            f"Complaint created: id={complaint.id}, user_id={user.id}, "
            f"type={complaint_type.value}, priority={priority.value}"
        )
        
        # Generate natural response using ResponseGenerator
        response_text = await self.response_generator.generate_complaint_response(
            complaint_data={
                "complaint_id": complaint.id,
                "type": complaint_type.value.replace('_', ' ').title(),
                "priority": priority.value,
                "sla_response_hours": self.SLA_RESPONSE_TIME[priority],
                "sla_resolution_hours": self.SLA_RESOLUTION_TIME[priority],
                "booking_number": booking.booking_number if booking else None,
                "is_critical": priority == ComplaintPriority.CRITICAL
            },
            conversation_history=None,  # TODO: Pass conversation history from coordinator
            user_name=user.first_name
        )

        return {
            "response": response_text,
            "action_taken": "complaint_created",
            "metadata": {
                "complaint_id": complaint.id,
                "complaint_type": complaint_type.value,
                "priority": priority.value,
                "status": ComplaintStatus.OPEN.value,
                "response_due_at": response_due_at.isoformat(),
                "resolution_due_at": resolution_due_at.isoformat(),
                "booking_id": booking.id if booking else None,
                "booking_number": booking.booking_number if booking else None
            }
        }
    
    async def _get_complaint_status(
        self,
        user: User,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get complaint status
        
        Args:
            user: Current user
            entities: Extracted entities (complaint_id)
        
        Returns:
            Response dict with complaint status
        """
        complaint_id = entities.get("complaint_id")
        
        if not complaint_id:
            return {
                "response": "Please provide your complaint ID to check the status.",
                "action_taken": "missing_entity",
                "metadata": {"missing": "complaint_id"}
            }
        
        # Get complaint
        result = await self.db.execute(
            select(Complaint).where(
                Complaint.id == int(complaint_id),
                Complaint.user_id == user.id
            )
        )
        complaint = result.scalar_one_or_none()
        
        if not complaint:
            return {
                "response": f"❌ Complaint #{complaint_id} not found.",
                "action_taken": "complaint_not_found",
                "metadata": {"complaint_id": complaint_id}
            }
        
        # Build status response
        response_parts = [
            f"📋 Complaint Status - #{complaint.id}",
            f"\n   • Type: {complaint.complaint_type.value.replace('_', ' ').title()}",
            f"   • Priority: {complaint.priority.value.upper()}",
            f"   • Status: {complaint.status.value.upper()}",
            f"   • Created: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if complaint.assigned_at:
            response_parts.append(f"   • Assigned: {complaint.assigned_at.strftime('%Y-%m-%d %H:%M')}")
        
        if complaint.resolved_at:
            response_parts.append(f"   • Resolved: {complaint.resolved_at.strftime('%Y-%m-%d %H:%M')}")
            if complaint.resolution:
                response_parts.append(f"\n✅ Resolution: {complaint.resolution}")
        else:
            response_parts.append(f"\n⏰ Expected Resolution: {complaint.resolution_due_at.strftime('%Y-%m-%d %H:%M')}")
        
        return {
            "response": "\n".join(response_parts),
            "action_taken": "complaint_status_retrieved",
            "metadata": complaint.to_dict()
        }
    
    async def _add_complaint_update(
        self,
        user: User,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add update/comment to complaint
        
        Args:
            user: Current user
            entities: Extracted entities (complaint_id, comment)
        
        Returns:
            Response dict
        """
        complaint_id = entities.get("complaint_id")
        comment = entities.get("comment")
        
        if not complaint_id or not comment:
            return {
                "response": "Please provide the complaint ID and your comment.",
                "action_taken": "missing_entity",
                "metadata": {"missing": "complaint_id or comment"}
            }
        
        # Verify complaint exists and belongs to user
        result = await self.db.execute(
            select(Complaint).where(
                Complaint.id == int(complaint_id),
                Complaint.user_id == user.id
            )
        )
        complaint = result.scalar_one_or_none()
        
        if not complaint:
            return {
                "response": f"❌ Complaint #{complaint_id} not found.",
                "action_taken": "complaint_not_found",
                "metadata": {"complaint_id": complaint_id}
            }
        
        # Add update
        update = ComplaintUpdate(
            complaint_id=complaint.id,
            user_id=user.id,
            comment=comment,
            is_internal=False
        )
        
        self.db.add(update)
        await self.db.commit()
        
        return {
            "response": f"✅ Your comment has been added to complaint #{complaint_id}. Our team will review it.",
            "action_taken": "complaint_updated",
            "metadata": {
                "complaint_id": complaint.id,
                "update_id": update.id
            }
        }

    async def _get_booking(self, booking_id: int, user: User) -> Booking:
        """
        Get booking by ID for the current user

        Args:
            booking_id: Booking ID
            user: Current user

        Returns:
            Booking object or None
        """
        result = await self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    def _map_complaint_type(self, complaint_type_str: str) -> ComplaintType:
        """
        Map complaint type string to enum

        Args:
            complaint_type_str: Complaint type string

        Returns:
            ComplaintType enum
        """
        type_mapping = {
            "service_quality": ComplaintType.SERVICE_QUALITY,
            "service quality": ComplaintType.SERVICE_QUALITY,
            "quality": ComplaintType.SERVICE_QUALITY,
            "provider_behavior": ComplaintType.PROVIDER_BEHAVIOR,
            "provider behavior": ComplaintType.PROVIDER_BEHAVIOR,
            "behavior": ComplaintType.PROVIDER_BEHAVIOR,
            "billing": ComplaintType.BILLING,
            "payment": ComplaintType.BILLING,
            "charge": ComplaintType.BILLING,
            "delay": ComplaintType.DELAY,
            "late": ComplaintType.DELAY,
            "cancellation_issue": ComplaintType.CANCELLATION_ISSUE,
            "cancellation issue": ComplaintType.CANCELLATION_ISSUE,
            "cancellation": ComplaintType.CANCELLATION_ISSUE,
            "refund_issue": ComplaintType.REFUND_ISSUE,
            "refund issue": ComplaintType.REFUND_ISSUE,
            "refund": ComplaintType.REFUND_ISSUE,
            "other": ComplaintType.OTHER,
        }

        return type_mapping.get(complaint_type_str.lower(), ComplaintType.OTHER)

    def _calculate_priority(self, description: str, complaint_type: ComplaintType) -> ComplaintPriority:
        """
        Calculate complaint priority based on content and type

        Args:
            description: Complaint description
            complaint_type: Complaint type

        Returns:
            ComplaintPriority enum
        """
        description_lower = description.lower()

        # Check for critical keywords
        if any(keyword in description_lower for keyword in self.CRITICAL_KEYWORDS):
            return ComplaintPriority.CRITICAL

        # Check for high priority keywords
        if any(keyword in description_lower for keyword in self.HIGH_KEYWORDS):
            return ComplaintPriority.HIGH

        # Type-based priority
        if complaint_type in [ComplaintType.REFUND_ISSUE, ComplaintType.BILLING]:
            return ComplaintPriority.HIGH
        elif complaint_type in [ComplaintType.SERVICE_QUALITY, ComplaintType.PROVIDER_BEHAVIOR]:
            return ComplaintPriority.MEDIUM
        else:
            return ComplaintPriority.LOW

