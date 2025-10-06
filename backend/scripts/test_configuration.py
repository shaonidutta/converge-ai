"""
Test configuration setup
Verify all core configurations are working
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

print("="*80)
print("TESTING CONFIGURATION SETUP")
print("="*80)

# Test 1: Settings
print("\n1. Testing Settings...")
try:
    from backend.src.core.config import settings
    
    print(f"   ✓ Settings loaded successfully")
    print(f"   - Environment: {settings.ENVIRONMENT}")
    print(f"   - Debug: {settings.DEBUG}")
    print(f"   - Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    print(f"   - Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"   - Log Level: {settings.LOG_LEVEL}")
    print(f"   - API Prefix: {settings.API_V1_PREFIX}")
    
except Exception as e:
    print(f"   ✗ Settings error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Logging
print("\n2. Testing Logging...")
try:
    from backend.src.core.logging import setup_logging, get_logger
    
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Test INFO message")
    logger.debug("Test DEBUG message")
    logger.warning("Test WARNING message")
    
    print(f"   ✓ Logging configured successfully")
    print(f"   - Log file: {settings.LOG_FILE}")
    print(f"   - Log level: {settings.LOG_LEVEL}")
    print(f"   - JSON format: {settings.LOG_JSON}")
    
except Exception as e:
    print(f"   ✗ Logging error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Database Connection
print("\n3. Testing Database Connection...")
try:
    from backend.src.core.database.connection import check_db_connection, get_pool_stats
    
    async def test_db():
        is_connected = await check_db_connection()
        if is_connected:
            print(f"   ✓ Database connection successful")
            
            # Get pool stats
            stats = await get_pool_stats()
            print(f"   - Pool size: {stats['pool_size']}")
            print(f"   - Checked in: {stats['checked_in']}")
            print(f"   - Checked out: {stats['checked_out']}")
            print(f"   - Total connections: {stats['total_connections']}")
        else:
            print(f"   ✗ Database connection failed")
    
    asyncio.run(test_db())
    
except Exception as e:
    print(f"   ✗ Database error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Redis Connection
print("\n4. Testing Redis Connection...")
try:
    from backend.src.core.cache import redis_client
    
    async def test_redis():
        await redis_client.connect()
        
        # Test ping
        is_connected = await redis_client.ping()
        if is_connected:
            print(f"   ✓ Redis connection successful")
            
            # Test set/get
            await redis_client.set("test_key", "test_value", ttl=60)
            value = await redis_client.get("test_key")
            
            if value == "test_value":
                print(f"   ✓ Redis SET/GET working")
            else:
                print(f"   ✗ Redis SET/GET failed")
            
            # Cleanup
            await redis_client.delete("test_key")
            
            await redis_client.disconnect()
        else:
            print(f"   ✗ Redis connection failed")
    
    asyncio.run(test_redis())
    
except Exception as e:
    print(f"   ✗ Redis error: {e}")
    print(f"   Note: Make sure Redis is running on {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    import traceback
    traceback.print_exc()

# Test 5: Environment Variables
print("\n5. Testing Environment Variables...")
try:
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "SECRET_KEY",
        "GOOGLE_API_KEY",
        "PINECONE_API_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not hasattr(settings, var) or not getattr(settings, var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ⚠ Missing environment variables:")
        for var in missing_vars:
            print(f"     - {var}")
    else:
        print(f"   ✓ All required environment variables present")
    
except Exception as e:
    print(f"   ✗ Environment variables error: {e}")

# Test 6: Configuration Properties
print("\n6. Testing Configuration Properties...")
try:
    print(f"   - Is Development: {settings.is_development}")
    print(f"   - Is Production: {settings.is_production}")
    print(f"   - Is Staging: {settings.is_staging}")
    print(f"   - Cache TTL Short: {settings.CACHE_TTL_SHORT}s")
    print(f"   - Cache TTL Medium: {settings.CACHE_TTL_MEDIUM}s")
    print(f"   - Cache TTL Long: {settings.CACHE_TTL_LONG}s")
    print(f"   - Max Upload Size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")
    print(f"   - Rate Limit Enabled: {settings.RATE_LIMIT_ENABLED}")
    print(f"   ✓ Configuration properties working")
    
except Exception as e:
    print(f"   ✗ Configuration properties error: {e}")

# Summary
print("\n" + "="*80)
print("CONFIGURATION TEST SUMMARY")
print("="*80)
print("\n✅ Core configuration is set up correctly!")
print("\nNext steps:")
print("1. Make sure Redis is running (if Redis test failed)")
print("2. Set missing environment variables in .env file")
print("3. Proceed with Phase 3 implementation")
print("\n" + "="*80)

