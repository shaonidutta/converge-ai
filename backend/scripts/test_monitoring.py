"""
Test script to verify Prometheus metrics are working

This script:
1. Checks if metrics endpoint is accessible
2. Verifies metrics are being collected
3. Tests health check endpoints
"""
import asyncio
import httpx
import sys


async def test_metrics_endpoint():
    """Test /api/v1/metrics endpoint"""
    print("\n🔍 Testing Metrics Endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/metrics")
            
            if response.status_code == 200:
                print("✅ Metrics endpoint is accessible")
                
                # Check if metrics are present
                content = response.text
                metrics_to_check = [
                    "http_requests_total",
                    "http_request_duration_seconds",
                    "agent_executions_total",
                    "llm_requests_total",
                    "db_queries_total",
                    "rag_retrievals_total"
                ]
                
                found_metrics = []
                for metric in metrics_to_check:
                    if metric in content:
                        found_metrics.append(metric)
                
                print(f"✅ Found {len(found_metrics)}/{len(metrics_to_check)} expected metrics")
                
                if len(found_metrics) < len(metrics_to_check):
                    missing = set(metrics_to_check) - set(found_metrics)
                    print(f"⚠️  Missing metrics: {missing}")
                
                return True
            else:
                print(f"❌ Metrics endpoint returned {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ Error accessing metrics endpoint: {e}")
        return False


async def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🔍 Testing Health Endpoints...")
    
    endpoints = [
        "/health",
        "/api/v1/health",
        "/api/v1/health/live",
        "/api/v1/health/ready"
    ]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"http://localhost:8000{endpoint}")
                
                if response.status_code in [200, 503]:
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                    results.append(True)
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    results.append(False)
            
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                results.append(False)
    
    return all(results)


async def test_prometheus_scraping():
    """Test if Prometheus can scrape metrics"""
    print("\n🔍 Testing Prometheus Scraping...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Check Prometheus targets
            response = await client.get("http://localhost:9090/api/v1/targets")
            
            if response.status_code == 200:
                data = response.json()
                targets = data.get("data", {}).get("activeTargets", [])
                
                convergeai_target = None
                for target in targets:
                    if "convergeai" in target.get("labels", {}).get("job", ""):
                        convergeai_target = target
                        break
                
                if convergeai_target:
                    health = convergeai_target.get("health", "unknown")
                    if health == "up":
                        print("✅ Prometheus is successfully scraping ConvergeAI metrics")
                        return True
                    else:
                        print(f"⚠️  Prometheus target health: {health}")
                        print(f"   Last error: {convergeai_target.get('lastError', 'N/A')}")
                        return False
                else:
                    print("⚠️  ConvergeAI target not found in Prometheus")
                    return False
            else:
                print(f"❌ Prometheus API returned {response.status_code}")
                return False
    
    except Exception as e:
        print(f"⚠️  Could not connect to Prometheus: {e}")
        print("   Make sure Prometheus is running: docker-compose -f deployment/docker-compose.monitoring.yml up -d")
        return False


async def test_grafana_connection():
    """Test if Grafana is accessible"""
    print("\n🔍 Testing Grafana Connection...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/api/health")
            
            if response.status_code == 200:
                print("✅ Grafana is accessible")
                print("   URL: http://localhost:3000")
                print("   Username: admin")
                print("   Password: admin")
                return True
            else:
                print(f"❌ Grafana returned {response.status_code}")
                return False
    
    except Exception as e:
        print(f"⚠️  Could not connect to Grafana: {e}")
        print("   Make sure Grafana is running: docker-compose -f deployment/docker-compose.monitoring.yml up -d")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 ConvergeAI Monitoring Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test metrics endpoint
    results.append(await test_metrics_endpoint())
    
    # Test health endpoints
    results.append(await test_health_endpoints())
    
    # Test Prometheus
    results.append(await test_prometheus_scraping())
    
    # Test Grafana
    results.append(await test_grafana_connection())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

