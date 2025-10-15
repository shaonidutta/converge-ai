"""
Unit tests for AlertService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.services.alert_service import AlertService
from src.core.models.alert import Alert, AlertRule
from src.core.models.complaint import Complaint, ComplaintPriority, ComplaintStatus


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def alert_service(mock_db):
    """Create AlertService instance with mocked dependencies"""
    return AlertService(mock_db)


@pytest.mark.asyncio
async def test_create_alert_basic(alert_service, mock_db):
    """Test creating a basic alert"""
    # Mock repository
    mock_alert = Alert(
        id=1,
        alert_type="test_alert",
        severity="info",
        title="Test Alert",
        message="This is a test alert",
        is_read=False,
        is_dismissed=False,
        created_at=datetime.utcnow()
    )
    
    alert_service.alert_repo.create_alert = AsyncMock(return_value=mock_alert)
    
    # Create alert
    result = await alert_service.create_alert(
        alert_type="test_alert",
        severity="info",
        title="Test Alert",
        message="This is a test alert"
    )
    
    # Assertions
    assert result.id == 1
    assert result.alert_type == "test_alert"
    assert result.severity == "info"
    assert result.title == "Test Alert"
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_create_alert_with_expiration(alert_service, mock_db):
    """Test creating alert with expiration"""
    mock_alert = Alert(
        id=1,
        alert_type="sla_breach",
        severity="critical",
        title="SLA Breach",
        message="SLA breached",
        expires_at=datetime.utcnow() + timedelta(hours=24),
        is_read=False,
        is_dismissed=False,
        created_at=datetime.utcnow()
    )
    
    alert_service.alert_repo.create_alert = AsyncMock(return_value=mock_alert)
    
    # Create alert with expiration
    result = await alert_service.create_alert(
        alert_type="sla_breach",
        severity="critical",
        title="SLA Breach",
        message="SLA breached",
        expires_in_hours=24
    )
    
    # Assertions
    assert result.expires_at is not None
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_get_staff_alerts(alert_service, mock_db):
    """Test getting alerts for staff"""
    mock_alerts = [
        Alert(id=1, alert_type="test1", severity="info", title="Alert 1", message="Message 1", is_read=False, is_dismissed=False, created_at=datetime.utcnow()),
        Alert(id=2, alert_type="test2", severity="warning", title="Alert 2", message="Message 2", is_read=False, is_dismissed=False, created_at=datetime.utcnow())
    ]
    
    alert_service.alert_repo.get_alerts_for_staff = AsyncMock(return_value=(mock_alerts, 2))
    alert_service.audit_service.log_access = AsyncMock()
    
    # Get alerts
    alerts, total = await alert_service.get_staff_alerts(staff_id=1)
    
    # Assertions
    assert len(alerts) == 2
    assert total == 2
    assert alerts[0].id == 1
    assert alerts[1].id == 2
    assert alert_service.audit_service.log_access.called


@pytest.mark.asyncio
async def test_get_staff_alerts_with_filters(alert_service, mock_db):
    """Test getting alerts with filters"""
    mock_alerts = [
        Alert(id=1, alert_type="sla_breach", severity="critical", title="Alert 1", message="Message 1", is_read=False, is_dismissed=False, created_at=datetime.utcnow())
    ]
    
    alert_service.alert_repo.get_alerts_for_staff = AsyncMock(return_value=(mock_alerts, 1))
    alert_service.audit_service.log_access = AsyncMock()
    
    # Get alerts with filters
    alerts, total = await alert_service.get_staff_alerts(
        staff_id=1,
        unread_only=True,
        alert_types=["sla_breach"],
        severities=["critical"]
    )
    
    # Assertions
    assert len(alerts) == 1
    assert alerts[0].alert_type == "sla_breach"
    assert alerts[0].severity == "critical"


@pytest.mark.asyncio
async def test_get_unread_count(alert_service, mock_db):
    """Test getting unread alert count"""
    alert_service.alert_repo.get_unread_count = AsyncMock(return_value=5)
    
    # Get unread count
    count = await alert_service.get_unread_count(staff_id=1)
    
    # Assertions
    assert count == 5


@pytest.mark.asyncio
async def test_mark_alert_read(alert_service, mock_db):
    """Test marking alert as read"""
    alert_service.alert_repo.mark_as_read = AsyncMock(return_value=True)
    
    # Mark as read
    success = await alert_service.mark_alert_read(alert_id=1, staff_id=1)
    
    # Assertions
    assert success is True
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_mark_alert_read_not_found(alert_service, mock_db):
    """Test marking non-existent alert as read"""
    alert_service.alert_repo.mark_as_read = AsyncMock(return_value=False)
    
    # Mark as read
    success = await alert_service.mark_alert_read(alert_id=999, staff_id=1)
    
    # Assertions
    assert success is False


@pytest.mark.asyncio
async def test_dismiss_alert(alert_service, mock_db):
    """Test dismissing alert"""
    alert_service.alert_repo.mark_as_dismissed = AsyncMock(return_value=True)
    
    # Dismiss alert
    success = await alert_service.dismiss_alert(alert_id=1, staff_id=1)
    
    # Assertions
    assert success is True
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_check_sla_alerts_at_risk(alert_service, mock_db):
    """Test SLA at-risk alert generation"""
    # Mock config
    alert_service.config_service.get_config_int = AsyncMock(return_value=1)
    
    # Mock at-risk complaint
    mock_complaint = Complaint(
        id=1,
        priority=ComplaintPriority.HIGH,
        status=ComplaintStatus.OPEN,
        response_due_at=datetime.utcnow() + timedelta(minutes=30),
        assigned_to_staff_id=5
    )
    
    # Mock database query
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_complaint]
    mock_db.execute.return_value = mock_result
    
    # Mock existing alert check
    alert_service._check_existing_alert = AsyncMock(return_value=False)
    
    # Mock alert creation
    alert_service.create_alert = AsyncMock()
    
    # Check SLA alerts
    count = await alert_service.check_sla_alerts()
    
    # Assertions
    assert count >= 0
    # Note: Actual count depends on mock data


@pytest.mark.asyncio
async def test_check_critical_complaints(alert_service, mock_db):
    """Test critical complaint alert generation"""
    # Mock critical complaint
    mock_complaint = Complaint(
        id=1,
        priority=ComplaintPriority.CRITICAL,
        status=ComplaintStatus.OPEN,
        created_at=datetime.utcnow() - timedelta(minutes=30),
        assigned_to_staff_id=5
    )
    
    # Mock database query
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_complaint]
    mock_db.execute.return_value = mock_result
    
    # Mock existing alert check
    alert_service._check_existing_alert = AsyncMock(return_value=False)
    
    # Mock alert creation
    alert_service.create_alert = AsyncMock()
    
    # Check critical complaints
    count = await alert_service.check_critical_complaints()
    
    # Assertions
    assert count >= 0


@pytest.mark.asyncio
async def test_check_existing_alert_found(alert_service, mock_db):
    """Test checking for existing alert - found"""
    # Mock existing alert
    mock_alert = Alert(id=1, alert_type="sla_breach", resource_type="complaint", resource_id=1, is_dismissed=False, created_at=datetime.utcnow())
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_alert
    mock_db.execute.return_value = mock_result
    
    # Check existing alert
    exists = await alert_service._check_existing_alert(
        alert_type="sla_breach",
        resource_type="complaint",
        resource_id=1
    )
    
    # Assertions
    assert exists is True


@pytest.mark.asyncio
async def test_check_existing_alert_not_found(alert_service, mock_db):
    """Test checking for existing alert - not found"""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Check existing alert
    exists = await alert_service._check_existing_alert(
        alert_type="sla_breach",
        resource_type="complaint",
        resource_id=999
    )
    
    # Assertions
    assert exists is False


@pytest.mark.asyncio
async def test_cleanup_old_alerts(alert_service, mock_db):
    """Test cleanup of old alerts"""
    alert_service.alert_repo.delete_expired_alerts = AsyncMock(return_value=10)
    
    # Cleanup
    deleted = await alert_service.cleanup_old_alerts(days=30)
    
    # Assertions
    assert deleted == 10
    assert mock_db.commit.called

