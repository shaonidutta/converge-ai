#!/usr/bin/env python3
"""Test ServiceNameResolver directly"""

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

from src.services.service_name_resolver import ServiceNameResolver

async def test_resolver():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL.startswith('mysql+pymysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql+pymysql://', 'mysql+aiomysql://')
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        resolver = ServiceNameResolver(session)
        
        # Test 1: "kitchen cleaning"
        print("=" * 80)
        print("Test 1: 'kitchen cleaning'")
        print("=" * 80)
        result = await resolver.resolve("kitchen cleaning", {})
        print(f"Resolved: {result.resolved}")
        if result.resolved:
            print(f"Category ID: {result.category_id}")
            print(f"Subcategory ID: {result.subcategory_id}")
            print(f"Subcategory Name: {result.subcategory_name}")
            print(f"Confidence: {result.confidence}")
            print(f"Method: {result.method}")
        else:
            print(f"Error: {result.error_message}")
        print()
        
        # Test 2: "cleaning"
        print("=" * 80)
        print("Test 2: 'cleaning'")
        print("=" * 80)
        result = await resolver.resolve("cleaning", {})
        print(f"Resolved: {result.resolved}")
        if result.resolved:
            print(f"Category ID: {result.category_id}")
            print(f"Subcategory ID: {result.subcategory_id}")
            print(f"Category Name: {result.category_name}")
            print(f"Confidence: {result.confidence}")
            print(f"Method: {result.method}")
        else:
            print(f"Error: {result.error_message}")
        print()

asyncio.run(test_resolver())

