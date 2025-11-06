"""
Test script for analytics endpoints
"""
import asyncio
from src.core.database.connection import get_db
from src.services.ops_analytics_service import OpsAnalyticsService
from src.schemas.ops_analytics import TimeRange

async def test_all():
    async for db in get_db():
        try:
            service = OpsAnalyticsService(db)
            
            print('=== Testing All Analytics Endpoints ===\n')
            
            # Test KPIs
            print('1. KPIs Endpoint:')
            kpis = await service.get_kpis(TimeRange.WEEK)
            print(f'   Total Bookings: {kpis.total_bookings.value}')
            print(f'   Total Revenue: Rs.{kpis.total_revenue.value}')
            print(f'   Active Complaints: {kpis.active_complaints.value}\n')
            
            # Test Trends
            print('2. Trends Endpoint:')
            trends = await service.get_trends(TimeRange.WEEK)
            print(f'   Data points: {len(trends.data)}\n')
            
            # Test Categories
            print('3. Categories Endpoint:')
            categories = await service.get_category_distribution(TimeRange.WEEK)
            print(f'   Categories: {len(categories.data)}\n')
            
            # Test Status
            print('4. Status Endpoint:')
            status = await service.get_status_distribution(TimeRange.WEEK)
            print(f'   Status types: {len(status.data)}\n')
            
            # Test Performance
            print('5. Performance Endpoint:')
            performance = await service.get_performance_metrics(TimeRange.WEEK)
            print(f'   Metrics: {len(performance.data)}\n')
            
            print('SUCCESS: All 5 analytics endpoints working!')
            
        except Exception as e:
            print(f'ERROR: {e}')
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_all())

