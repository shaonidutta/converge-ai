"""
Unit tests for MetricsService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.services.metrics_service import MetricsService
from src.repositories.metrics_repository import MetricsRepository
from src.services.config_service import ConfigService
from src.services.audit_service import AuditService


class TestMetricsService:
    """Test suite for MetricsService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_config_service(self):
        """Mock config service"""
        service = AsyncMock(spec=ConfigService)
        service.get_config_int = AsyncMock(return_value=1)
        return service
    
    @pytest.fixture
    def mock_audit_service(self):
        """Mock audit service"""
        service = AsyncMock(spec=AuditService)
        service.log_access = AsyncMock()
        return service
    
    @pytest.fixture
    def metrics_service(self, mock_db, mock_config_service, mock_audit_service):
        """Create MetricsService instance with mocked dependencies"""
        return MetricsService(mock_db, mock_config_service, mock_audit_service)
    
    @pytest.mark.asyncio
    async def test_get_bookings_metrics(self, metrics_service):
        """Test getting bookings metrics"""
        # Mock repository methods
        metrics_service.repository.get_bookings_by_status = AsyncMock(return_value={
            "pending": 15,
            "confirmed": 23,
            "in_progress": 12,
            "completed": 145,
            "cancelled": 8
        })
        metrics_service.repository.get_bookings_count = AsyncMock(side_effect=[15, 87, 342])
        
        # Call method
        result = await metrics_service._get_bookings_metrics("all")
        
        # Assertions
        assert result["by_status"]["pending"] == 15
        assert result["by_status"]["completed"] == 145
        assert result["today"] == 15
        assert result["week"] == 87
        assert result["month"] == 342
        assert "growth_rate" in result
    
    @pytest.mark.asyncio
    async def test_get_complaints_metrics(self, metrics_service):
        """Test getting complaints metrics"""
        # Mock repository methods
        metrics_service.repository.get_complaints_by_priority = AsyncMock(return_value={
            "low": 45,
            "medium": 32,
            "high": 18,
            "critical": 5
        })
        metrics_service.repository.get_complaints_by_status = AsyncMock(return_value={
            "open": 23,
            "in_progress": 15,
            "resolved": 45,
            "closed": 12,
            "escalated": 5
        })
        metrics_service.repository.get_complaints_count = AsyncMock(return_value=8)
        metrics_service.repository.get_unresolved_complaints_count = AsyncMock(return_value=43)
        metrics_service.repository.get_average_resolution_time = AsyncMock(return_value=18.5)
        
        # Call method
        result = await metrics_service._get_complaints_metrics("all")
        
        # Assertions
        assert result["by_priority"]["critical"] == 5
        assert result["by_status"]["open"] == 23
        assert result["today"] == 8
        assert result["unresolved"] == 43
        assert result["avg_resolution_hours"] == 18.5
    
    @pytest.mark.asyncio
    async def test_get_sla_metrics(self, metrics_service):
        """Test getting SLA metrics"""
        # Mock repository methods
        metrics_service.repository.get_sla_at_risk_count = AsyncMock(return_value=5)
        metrics_service.repository.get_sla_breached_count = AsyncMock(return_value=2)
        metrics_service.repository.get_active_complaints_count = AsyncMock(return_value=38)
        metrics_service.repository.get_complaints_count = AsyncMock(return_value=100)
        metrics_service.repository.get_average_resolution_time = AsyncMock(return_value=18.5)
        
        # Call method
        result = await metrics_service._get_sla_metrics("all")
        
        # Assertions
        assert result["at_risk"] == 5
        assert result["breached"] == 2
        assert result["compliance_rate"] == 98.0  # (100-2)/100 * 100
        assert result["avg_resolution_hours"] == 18.5
    
    @pytest.mark.asyncio
    async def test_get_sla_metrics_zero_complaints(self, metrics_service):
        """Test SLA metrics with zero complaints"""
        # Mock repository methods
        metrics_service.repository.get_sla_at_risk_count = AsyncMock(return_value=0)
        metrics_service.repository.get_sla_breached_count = AsyncMock(return_value=0)
        metrics_service.repository.get_active_complaints_count = AsyncMock(return_value=0)
        metrics_service.repository.get_complaints_count = AsyncMock(return_value=0)
        metrics_service.repository.get_average_resolution_time = AsyncMock(return_value=None)
        
        # Call method
        result = await metrics_service._get_sla_metrics("all")
        
        # Assertions
        assert result["compliance_rate"] == 100.0  # Default when no complaints
    
    @pytest.mark.asyncio
    async def test_get_revenue_metrics(self, metrics_service):
        """Test getting revenue metrics"""
        # Mock repository methods
        metrics_service.repository.get_revenue_by_status = AsyncMock(return_value={
            "pending": 0.0,
            "confirmed": 0.0,
            "in_progress": 45000.00,
            "completed": 1205000.00,
            "cancelled": 0.0
        })
        metrics_service.repository.get_total_revenue = AsyncMock(side_effect=[
            1250000.00,  # total
            45000.00,    # today
            285000.00,   # week
            1250000.00   # month
        ])
        metrics_service.repository.get_average_order_value = AsyncMock(return_value=3654.76)
        
        # Call method
        result = await metrics_service._get_revenue_metrics("all")
        
        # Assertions
        assert result["total"] == 1250000.00
        assert result["by_status"]["completed"] == 1205000.00
        assert result["today"] == 45000.00
        assert result["week"] == 285000.00
        assert result["month"] == 1250000.00
        assert result["average_order_value"] == 3654.76
    
    @pytest.mark.asyncio
    async def test_get_realtime_metrics(self, metrics_service):
        """Test getting real-time metrics"""
        # Mock repository methods
        metrics_service.repository.get_active_bookings_count = AsyncMock(return_value=12)
        metrics_service.repository.get_pending_bookings_count = AsyncMock(return_value=38)
        metrics_service.repository.get_active_complaints_count = AsyncMock(return_value=38)
        metrics_service.repository.get_critical_complaints_count = AsyncMock(return_value=5)
        metrics_service.repository.get_staff_workload = AsyncMock(return_value={
            "total_staff": 8,
            "staff_assignments": []
        })
        
        # Call method
        result = await metrics_service._get_realtime_metrics()
        
        # Assertions
        assert result["active_bookings"] == 12
        assert result["pending_bookings"] == 38
        assert result["active_complaints"] == 38
        assert result["critical_complaints"] == 5
        assert result["staff_workload"]["total_staff"] == 8
    
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_all_groups(self, metrics_service):
        """Test getting all dashboard metrics"""
        # Mock all metric methods
        metrics_service._get_bookings_metrics = AsyncMock(return_value={"today": 15})
        metrics_service._get_complaints_metrics = AsyncMock(return_value={"today": 8})
        metrics_service._get_sla_metrics = AsyncMock(return_value={"at_risk": 5})
        metrics_service._get_revenue_metrics = AsyncMock(return_value={"total": 1250000.00})
        metrics_service._get_realtime_metrics = AsyncMock(return_value={"active_bookings": 12})
        
        # Call method
        result = await metrics_service.get_dashboard_metrics(
            staff_id=1,
            period="all",
            include_groups=None  # Should include all groups
        )
        
        # Assertions
        assert "period" in result
        assert "generated_at" in result
        assert "bookings" in result
        assert "complaints" in result
        assert "sla" in result
        assert "revenue" in result
        assert "realtime" in result
        assert result["period"] == "all"
        
        # Verify audit logging was called
        metrics_service.audit_service.log_access.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_specific_groups(self, metrics_service):
        """Test getting specific metric groups"""
        # Mock specific metric methods
        metrics_service._get_bookings_metrics = AsyncMock(return_value={"today": 15})
        metrics_service._get_complaints_metrics = AsyncMock(return_value={"today": 8})
        
        # Call method with specific groups
        result = await metrics_service.get_dashboard_metrics(
            staff_id=1,
            period="today",
            include_groups=["bookings", "complaints"]
        )
        
        # Assertions
        assert "bookings" in result
        assert "complaints" in result
        assert "sla" not in result
        assert "revenue" not in result
        assert "realtime" not in result
        assert result["period"] == "today"
    
    @pytest.mark.asyncio
    async def test_calculate_growth_rate(self, metrics_service):
        """Test growth rate calculation"""
        # Test positive growth
        growth = metrics_service._calculate_growth_rate(120, 100)
        assert growth == 20.0
        
        # Test negative growth
        growth = metrics_service._calculate_growth_rate(80, 100)
        assert growth == -20.0
        
        # Test zero previous (edge case)
        growth = metrics_service._calculate_growth_rate(100, 0)
        assert growth == 100.0
        
        # Test both zero
        growth = metrics_service._calculate_growth_rate(0, 0)
        assert growth == 0.0
    
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_period_filtering(self, metrics_service):
        """Test period filtering in dashboard metrics"""
        # Mock metric methods
        metrics_service._get_bookings_metrics = AsyncMock(return_value={"today": 15})
        
        # Test different periods
        for period in ["today", "week", "month", "all"]:
            result = await metrics_service.get_dashboard_metrics(
                staff_id=1,
                period=period,
                include_groups=["bookings"]
            )
            assert result["period"] == period

