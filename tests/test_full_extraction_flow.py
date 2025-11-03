"""
Test full extraction flow with database
"""
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.insert(0, 'backend')

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.services.entity_extractor import EntityExtractor, EntityType

async def test():
    # Create database session
    engine = create_async_engine(
        "mysql+aiomysql://admin:Converge%40123@ls-d157091fb9608cc702c3b9a33dec25bca625f14b.cstb7bwkbg8x.ap-south-1.rds.amazonaws.com/convergeai_db",
        echo=False
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create extractor with database
        extractor = EntityExtractor(db=session)
        
        # Test extraction
        test_input = "i want to book kitchen cleaning"
        print(f"\n=== Testing: '{test_input}' ===\n")
        
        # Clean the message
        cleaned = extractor._clean_conversational_prefixes(test_input)
        print(f"Cleaned: '{cleaned}'")
        
        # Extract service type
        result = extractor._extract_service_type(cleaned.lower())
        
        if result:
            print(f"\nExtraction Result:")
            print(f"  Entity Type: {result.entity_type}")
            print(f"  Entity Value: {result.entity_value}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Method: {result.extraction_method}")
            if result.metadata:
                print(f"  Metadata: {result.metadata}")
        else:
            print(f"  No match")
        
        # Now test with extract_from_follow_up
        print(f"\n=== Testing extract_from_follow_up ===\n")
        result2 = await extractor.extract_from_follow_up(
            message=test_input,
            expected_entity=EntityType.SERVICE_TYPE,
            context={"user_id": 1}
        )
        
        if result2:
            print(f"Extraction Result:")
            print(f"  Entity Type: {result2.entity_type}")
            print(f"  Entity Value: {result2.entity_value}")
            print(f"  Confidence: {result2.confidence}")
            print(f"  Method: {result2.extraction_method}")
            if result2.metadata:
                print(f"  Metadata: {result2.metadata}")
        else:
            print(f"  No match")

asyncio.run(test())

