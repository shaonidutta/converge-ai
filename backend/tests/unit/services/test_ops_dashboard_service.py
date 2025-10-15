"""
Unit tests for OpsDashboardService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from src.services.ops_dashboard_service import OpsDashboardService
from src.core.models import (
    PriorityQueue, User, Staff, Complaint, Booking,
    IntentType, ComplaintPriority, ComplaintStatus, BookingStatus
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_staff():
    """Mock staff user"""
    staff = MagicMock(spec=Staff)
    staff.id = 1
    staff.employee_id = "EMP001"
    staff.first_name = "John"
    staff.last_name = "Doe"
    staff.role = MagicMock()
    staff.role.permissions = []
    return staff


@pytest.fixture
def mock_priority_item():
    """Mock priority queue item"""
    item = MagicMock(spec=PriorityQueue)
    item.id = 1
    item.user_id = 100
    item.session_id = "sess_123"
    item.intent_type = IntentType.COMPLAINT
    item.confidence_score = 0.95
    item.priority_score = 85
    item.sentiment_score = -0.75
    item.message_snippet = "Very disappointed with service"
    item.is_reviewed = False
    item.reviewed_by_staff_id = None
    item.reviewed_by_staff = None
    item.reviewed_at = None
    item.action_taken = None
    item.created_at = datetime.now(timezone.utc)
    item.updated_at = datetime.now(timezone.utc)
    
    # Mock user
    item.user = MagicMock(spec=User)
    item.user.id = 100
    item.user.first_name = "Jane"
    item.user.last_name = "Smith"
    item.user.mobile = "9876543210"
    item.user.email = "jane@example.com"
    
    # Mock to_dict method
    item.to_dict.return_value = {
        "id": item.id,
        "user_id": item.user_id,
        "session_id": item.session_id,
        "intent_type": item.intent_type.value,
        "confidence_score": item.confidence_score,
        "priority_score": item.priority_score,
        "sentiment_score": item.sentiment_score,
        "message_snippet": item.message_snippet,
        "is_reviewed": item.is_reviewed,
        "reviewed_by_staff_id": item.reviewed_by_staff_id,
        "reviewed_at": item.reviewed_at,
        "action_taken": item.action_taken,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat()
    }
    
    return item


class TestOpsDashboardService:
    """Test suite for OpsDashboardService"""
    
    @pytest.mark.asyncio
    async def test_get_priority_queue_basic(self, mock_db, mock_staff, mock_priority_item):
        """Test basic priority queue retrieval"""
        service = OpsDashboardService(mock_db)
        
        # Mock repository methods
        with patch.object(service.priority_queue_repo, 'get_priority_items', return_value=[mock_priority_item]):
            with patch.object(service.priority_queue_repo, 'count_priority_items', return_value=1):
                with patch.object(service.config_service, 'get_config', return_value="pending"):
                    with patch.object(service.audit_service, 'log_priority_queue_access', return_value=AsyncMock()):
                        with patch.object(service, '_check_full_access_permission', return_value=False):
                            with patch.object(service, '_enrich_priority_item', return_value=mock_priority_item.to_dict()):
                                
                                result = await service.get_priority_queue(
                                    current_staff=mock_staff,
                                    skip=0,
                                    limit=20
                                )
        
        # Assertions
        assert result is not None
        assert "items" in result
        assert "total" in result
        assert "skip" in result
        assert "limit" in result
        assert "has_more" in result
        assert len(result["items"]) == 1
        assert result["total"] == 1
        assert result["skip"] == 0
        assert result["limit"] == 20
        assert result["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_check_full_access_permission_with_access(self, mock_db, mock_staff):
        """Test full access permission check - user has access"""
        service = OpsDashboardService(mock_db)
        
        # Mock permission
        mock_perm = MagicMock()
        mock_perm.name = "ops.full_access"
        mock_staff.role.permissions = [mock_perm]
        
        with patch.object(service, '_get_staff_permissions', return_value=["ops.full_access"]):
            has_access = await service._check_full_access_permission(mock_staff)
        
        assert has_access is True
    
    @pytest.mark.asyncio
    async def test_check_full_access_permission_without_access(self, mock_db, mock_staff):
        """Test full access permission check - user does not have access"""
        service = OpsDashboardService(mock_db)
        
        # Mock permission
        mock_perm = MagicMock()
        mock_perm.name = "ops.read"
        mock_staff.role.permissions = [mock_perm]
        
        with patch.object(service, '_get_staff_permissions', return_value=["ops.read"]):
            has_access = await service._check_full_access_permission(mock_staff)
        
        assert has_access is False
    
    def test_redact_pii_mobile(self, mock_db):
        """Test PII redaction for mobile number"""
        service = OpsDashboardService(mock_db)
        
        item_dict = {
            "user_mobile": "9876543210"
        }
        
        redacted = service._redact_pii(item_dict)
        
        assert redacted["user_mobile"] == "98****3210"
    
    def test_redact_pii_email(self, mock_db):
        """Test PII redaction for email"""
        service = OpsDashboardService(mock_db)
        
        item_dict = {
            "user_email": "jane@example.com"
        }
        
        redacted = service._redact_pii(item_dict)
        
        assert redacted["user_email"] == "j***@example.com"
    
    def test_redact_pii_name(self, mock_db):
        """Test PII redaction for name"""
        service = OpsDashboardService(mock_db)
        
        item_dict = {
            "user_name": "Jane Smith"
        }
        
        redacted = service._redact_pii(item_dict)
        
        assert redacted["user_name"] == "Jane S."
    
    def test_redact_pii_message_snippet(self, mock_db):
        """Test PII redaction for long message snippet"""
        service = OpsDashboardService(mock_db)
        
        long_message = "A" * 150
        item_dict = {
            "message_snippet": long_message
        }
        
        redacted = service._redact_pii(item_dict)
        
        assert len(redacted["message_snippet"]) == 103  # 100 chars + "..."
        assert redacted["message_snippet"].endswith("...")
    
    def test_build_filters(self, mock_db):
        """Test filter building"""
        service = OpsDashboardService(mock_db)
        
        filters = service._build_filters(
            status="pending",
            intent_type="complaint",
            priority_min=50,
            priority_max=100,
            date_from=datetime(2025, 1, 1),
            date_to=datetime(2025, 12, 31)
        )
        
        assert filters["status"] == "pending"
        assert filters["intent_type"] == "complaint"
        assert filters["priority_min"] == 50
        assert filters["priority_max"] == 100"
        assert filters["date_from"] == datetime(2025, 1, 1)
        assert filters["date_to"] == datetime(2025, 12, 31)
    
    def test_calculate_booking_priority(self, mock_db):
        """Test booking priority calculation"""
        service = OpsDashboardService(mock_db)
        
        # Pending booking - high priority
        booking = MagicMock(spec=Booking)
        booking.status = BookingStatus.PENDING
        assert service._calculate_booking_priority(booking) == "high"
        
        # Confirmed booking - medium priority
        booking.status = BookingStatus.CONFIRMED
        assert service._calculate_booking_priority(booking) == "medium"
        
        # Completed booking - low priority
        booking.status = BookingStatus.COMPLETED
        assert service._calculate_booking_priority(booking) == "low"
    
    def test_calculate_sla_risk_at_risk(self, mock_db):
        """Test SLA risk calculation - at risk"""
        service = OpsDashboardService(mock_db)
        
        # Complaint due in 30 minutes (within 1 hour buffer)
        complaint = MagicMock(spec=Complaint)
        complaint.response_due_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        assert service._calculate_sla_risk(complaint) is True
    
    def test_calculate_sla_risk_not_at_risk(self, mock_db):
        """Test SLA risk calculation - not at risk"""
        service = OpsDashboardService(mock_db)
        
        # Complaint due in 2 hours (outside 1 hour buffer)
        complaint = MagicMock(spec=Complaint)
        complaint.response_due_at = datetime.now(timezone.utc) + timedelta(hours=2)
        
        assert service._calculate_sla_risk(complaint) is False
    
    def test_calculate_sla_risk_no_due_date(self, mock_db):
        """Test SLA risk calculation - no due date"""
        service = OpsDashboardService(mock_db)
        
        complaint = MagicMock(spec=Complaint)
        complaint.response_due_at = None
        
        assert service._calculate_sla_risk(complaint) is False

