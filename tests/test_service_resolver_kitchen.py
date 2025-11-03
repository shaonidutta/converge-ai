import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_resolver():
    # Create database engine
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Replace mysql+pymysql with mysql+aiomysql for async support
    if "mysql+pymysql" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from src.services.service_dictionary import ServiceNameResolver
        
        resolver = ServiceNameResolver(session)
        
        # Test "kitchen cleaning"
        print("=" * 80)
        print("Testing: 'kitchen cleaning'")
        print("=" * 80)
        result = await resolver.resolve("kitchen cleaning", {})
        
        print(f"Resolved: {result.resolved}")
        print(f"Confidence: {result.confidence}")
        print(f"Method: {result.method}")
        print(f"Category ID: {result.category_id}")
        print(f"Category Name: {result.category_name}")
        print(f"Subcategory ID: {result.subcategory_id}")
        print(f"Subcategory Name: {result.subcategory_name}")
        print(f"Service Name: {result.service_name}")
        print(f"Rate Card ID: {result.rate_card_id}")
        print(f"Error: {result.error_message}")
        print()
        
        # Test "i want to book kitchen cleaning"
        print("=" * 80)
        print("Testing: 'i want to book kitchen cleaning'")
        print("=" * 80)
        result = await resolver.resolve("i want to book kitchen cleaning", {})
        
        print(f"Resolved: {result.resolved}")
        print(f"Confidence: {result.confidence}")
        print(f"Method: {result.method}")
        print(f"Category ID: {result.category_id}")
        print(f"Category Name: {result.category_name}")
        print(f"Subcategory ID: {result.subcategory_id}")
        print(f"Subcategory Name: {result.subcategory_name}")
        print(f"Service Name: {result.service_name}")
        print(f"Rate Card ID: {result.rate_card_id}")
        print(f"Error: {result.error_message}")
        print()

asyncio.run(test_resolver())

