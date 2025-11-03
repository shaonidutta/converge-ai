#!/usr/bin/env python3
"""Test EntityExtractor with database session"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# Load .env from backend directory FIRST before any imports
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from src.services.entity_extractor import EntityExtractor
from src.nlp.intent.config import EntityType

async def test_extractor():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL.startswith('mysql+pymysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql+pymysql://', 'mysql+aiomysql://')
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Initialize EntityExtractor with db session
        extractor = EntityExtractor(llm_client=None, db=session)
        
        print("=" * 80)
        print("EntityExtractor Initialization")
        print("=" * 80)
        print(f"service_resolver initialized: {extractor.service_resolver is not None}")
        print()
        
        if extractor.service_resolver:
            # Test 1: "kitchen cleaning"
            print("=" * 80)
            print("Test 1: Extracting SERVICE_TYPE from 'kitchen cleaning'")
            print("=" * 80)

            result = await extractor.extract_from_follow_up(
                message="kitchen cleaning",
                expected_entity=EntityType.SERVICE_TYPE,
                context={}
            )

            if result:
                print(f"✅ Extraction successful!")
                print(f"   Entity Type: {result.entity_type}")
                print(f"   Entity Value: {result.entity_value}")
                print(f"   Confidence: {result.confidence}")
                print(f"   Method: {result.extraction_method}")
                if result.metadata:
                    print(f"   Metadata keys: {list(result.metadata.keys())}")
                    if '_resolved_service' in result.metadata:
                        resolved = result.metadata['_resolved_service']
                        print(f"   Resolved Service:")
                        print(f"      category_id: {resolved.get('category_id')}")
                        print(f"      subcategory_id: {resolved.get('subcategory_id')}")
                        print(f"      subcategory_name: {resolved.get('subcategory_name')}")
            else:
                print("❌ Extraction failed")
            print()

            # Test 2: "i want to book kitchen cleaning"
            print("=" * 80)
            print("Test 2: Extracting SERVICE_TYPE from 'i want to book kitchen cleaning'")
            print("=" * 80)

            result = await extractor.extract_from_follow_up(
                message="i want to book kitchen cleaning",
                expected_entity=EntityType.SERVICE_TYPE,
                context={}
            )

            if result:
                print(f"✅ Extraction successful!")
                print(f"   Entity Type: {result.entity_type}")
                print(f"   Entity Value: {result.entity_value}")
                print(f"   Confidence: {result.confidence}")
                print(f"   Method: {result.extraction_method}")
                if result.metadata:
                    print(f"   Metadata keys: {list(result.metadata.keys())}")
                    if '_resolved_service' in result.metadata:
                        resolved = result.metadata['_resolved_service']
                        print(f"   Resolved Service:")
                        print(f"      category_id: {resolved.get('category_id')}")
                        print(f"      subcategory_id: {resolved.get('subcategory_id')}")
                        print(f"      subcategory_name: {resolved.get('subcategory_name')}")
            else:
                print("❌ Extraction failed")
        else:
            print("❌ ServiceNameResolver not initialized")

asyncio.run(test_extractor())

