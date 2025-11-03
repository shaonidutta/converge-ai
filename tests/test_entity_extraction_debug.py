"""
Debug entity extraction for kitchen cleaning
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# Load environment first
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from src.services.entity_extractor import EntityExtractor
from src.nlp.intent.config import EntityType

async def test_entity_extraction():
    DATABASE_URL = os.getenv('DATABASE_URL')
    # Convert to async URL
    if DATABASE_URL.startswith('mysql+pymysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql+pymysql://', 'mysql+aiomysql://')
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Initialize EntityExtractor
        extractor = EntityExtractor(db=session)
        
        print("="*80)
        print("Test 1: Extract SERVICE_TYPE from 'i want to book kitchen cleaning'")
        print("="*80)
        
        result1 = await extractor.extract_from_follow_up(
            message="i want to book kitchen cleaning",
            expected_entity=EntityType.SERVICE_TYPE,
            context={}
        )
        
        if result1:
            print(f"✅ Extracted: {result1.entity_value}")
            print(f"   Confidence: {result1.confidence}")
            print(f"   Method: {result1.extraction_method}")
            print(f"   Normalized: {result1.normalized_value}")
            if result1.metadata:
                print(f"   Metadata: {result1.metadata}")
        else:
            print("❌ No extraction result")
        
        print("\n" + "="*80)
        print("Test 2: Extract SERVICE_SUBCATEGORY from 'kitchen cleaning'")
        print("="*80)
        
        # Simulate available subcategories from Home Cleaning category
        available_subcategories = [
            {"id": 1, "name": "Deep Cleaning"},
            {"id": 2, "name": "Regular Cleaning"},
            {"id": 3, "name": "Kitchen Cleaning"},
            {"id": 4, "name": "Bathroom Cleaning"},
            {"id": 5, "name": "Sofa Cleaning"},
            {"id": 6, "name": "Carpet Cleaning"},
            {"id": 7, "name": "Window Cleaning"},
            {"id": 8, "name": "Move-in/Move-out Cleaning"}
        ]
        
        result2 = await extractor.extract_from_follow_up(
            message="kitchen cleaning",
            expected_entity=EntityType.SERVICE_SUBCATEGORY,
            context={"available_subcategories": available_subcategories}
        )
        
        if result2:
            print(f"✅ Extracted: {result2.entity_value}")
            print(f"   Confidence: {result2.confidence}")
            print(f"   Method: {result2.extraction_method}")
            print(f"   Normalized: {result2.normalized_value}")
            if result2.metadata:
                print(f"   Metadata: {result2.metadata}")
        else:
            print("❌ No extraction result")
        
        print("\n" + "="*80)
        print("Test 3: Extract SERVICE_SUBCATEGORY from '3'")
        print("="*80)
        
        result3 = await extractor.extract_from_follow_up(
            message="3",
            expected_entity=EntityType.SERVICE_SUBCATEGORY,
            context={"available_subcategories": available_subcategories}
        )
        
        if result3:
            print(f"✅ Extracted: {result3.entity_value}")
            print(f"   Confidence: {result3.confidence}")
            print(f"   Method: {result3.extraction_method}")
            print(f"   Normalized: {result3.normalized_value}")
            if result3.metadata:
                print(f"   Metadata: {result3.metadata}")
        else:
            print("❌ No extraction result")

asyncio.run(test_entity_extraction())

