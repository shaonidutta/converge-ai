#!/usr/bin/env python3
"""
Script to check actual services and subcategories in the database
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.models.category import Category, Subcategory
from src.core.models.rate_card import RateCard

async def check_services():
    """Check all services and subcategories in the database"""

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return []

    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔍 CHECKING ACTUAL SERVICES IN DATABASE")
            print("=" * 60)
            
            # Get all categories with subcategory counts
            result = await session.execute(
                select(
                    Category.id,
                    Category.name,
                    Category.slug,
                    Category.is_active,
                    func.count(Subcategory.id).label('subcategory_count')
                )
                .outerjoin(Subcategory, Category.id == Subcategory.category_id)
                .where(Category.is_active == True)
                .group_by(Category.id, Category.name, Category.slug, Category.is_active)
                .order_by(Category.display_order, Category.name)
            )
            
            categories = result.all()
            
            print(f"📋 FOUND {len(categories)} ACTIVE CATEGORIES:")
            print()
            
            total_subcategories = 0
            service_summary = []
            
            for i, (cat_id, cat_name, cat_slug, is_active, subcat_count) in enumerate(categories, 1):
                print(f"{i:2d}. {cat_name} ({subcat_count} subcategories)")
                service_summary.append({
                    'id': cat_id,
                    'name': cat_name,
                    'slug': cat_slug,
                    'subcategory_count': subcat_count
                })
                total_subcategories += subcat_count
                
                # Get subcategories for this category
                subcat_result = await session.execute(
                    select(
                        Subcategory.id,
                        Subcategory.name,
                        Subcategory.slug,
                        func.count(RateCard.id).label('rate_card_count')
                    )
                    .outerjoin(RateCard, Subcategory.id == RateCard.subcategory_id)
                    .where(
                        Subcategory.category_id == cat_id,
                        Subcategory.is_active == True
                    )
                    .group_by(Subcategory.id, Subcategory.name, Subcategory.slug)
                    .order_by(Subcategory.display_order, Subcategory.name)
                )
                
                subcategories = subcat_result.all()
                for subcat_id, subcat_name, subcat_slug, rate_count in subcategories:
                    print(f"    - {subcat_name} (ID: {subcat_id}, Rate Cards: {rate_count})")
                
                print()
            
            print("=" * 60)
            print(f"📊 SUMMARY:")
            print(f"   Total Categories: {len(categories)}")
            print(f"   Total Subcategories: {total_subcategories}")
            print()
            
            # Compare with user's list
            user_list = [
                ("Home Cleaning", 8),
                ("AC Services", 1), 
                ("Appliance Repair", 8),
                ("Plumbing", 7),
                ("Electrical", 7),
                ("Carpentry", 7),
                ("Painting", 5),
                ("Pest Control", 6),
                ("Water Purifier", 4),
                ("Car Care", 5),
                ("Salon for Women", 8),
                ("Salon for Men", 6),
                ("Packers and Movers", 5)
            ]
            
            print("🔍 COMPARISON WITH USER'S LIST:")
            print("=" * 60)
            
            # Create lookup for actual services
            actual_services = {service['name'].lower(): service for service in service_summary}
            
            matches = 0
            mismatches = []
            
            for user_service, user_count in user_list:
                # Try to find matching service
                found = False
                for actual_service in service_summary:
                    if (user_service.lower() in actual_service['name'].lower() or 
                        actual_service['name'].lower() in user_service.lower()):
                        found = True
                        actual_count = actual_service['subcategory_count']
                        status = "✅ MATCH" if actual_count == user_count else f"❌ MISMATCH (DB: {actual_count})"
                        print(f"{user_service:20} | User: {user_count:2d} | DB: {actual_count:2d} | {status}")
                        if actual_count == user_count:
                            matches += 1
                        else:
                            mismatches.append((user_service, user_count, actual_count))
                        break
                
                if not found:
                    print(f"{user_service:20} | User: {user_count:2d} | DB: -- | ❌ NOT FOUND")
                    mismatches.append((user_service, user_count, 0))
            
            print()
            print(f"📊 COMPARISON RESULTS:")
            print(f"   Matches: {matches}/{len(user_list)}")
            print(f"   Mismatches: {len(mismatches)}")
            
            if mismatches:
                print()
                print("❌ MISMATCHES FOUND:")
                for service, user_count, db_count in mismatches:
                    print(f"   - {service}: User says {user_count}, DB has {db_count}")
            
            return service_summary
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_services())
