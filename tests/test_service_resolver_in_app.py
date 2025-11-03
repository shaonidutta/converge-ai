"""
Test ServiceNameResolver in application context
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv('backend/.env')

async def test_service_resolver():
    # Get database URL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL.startswith('mysql+pymysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql+pymysql://', 'mysql+aiomysql://')
    
    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Import ServiceNameResolver
        import sys
        sys.path.insert(0, 'backend')
        from src.services.service_name_resolver import ServiceNameResolver

        # Create resolver
        resolver = ServiceNameResolver(session)
        
        # Test resolution
        print("\n=== Testing ServiceNameResolver ===\n")
        
        test_cases = [
            "kitchen cleaning",
            "i want to book kitchen cleaning",
            "cleaning",
            "home cleaning"
        ]
        
        for test_input in test_cases:
            print(f"Input: '{test_input}'")
            result = await resolver.resolve(test_input, {})
            print(f"  Resolved: {result.resolved}")
            if result.resolved:
                print(f"  Category ID: {result.category_id}")
                print(f"  Subcategory ID: {result.subcategory_id}")
                print(f"  Service Name: {result.service_name or result.subcategory_name or result.category_name}")
                print(f"  Confidence: {result.confidence}")
                print(f"  Method: {result.method}")
            else:
                print(f"  Error: {result.error_message}")
            print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_service_resolver())

