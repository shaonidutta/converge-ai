#!/usr/bin/env python3
"""
Quick script to create a test operations staff user
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database.connection import AsyncSessionLocal
from src.core.models.staff import Staff
from src.core.models.role import Role
from src.core.security.password import hash_password
from datetime import date


async def create_test_ops_user():
    """Create a test operations staff user"""
    print("\n" + "="*70)
    print("  CREATING TEST OPERATIONS STAFF USER")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if test staff already exists (by email or employee_id)
            result = await db.execute(
                select(Staff).where(
                    (Staff.email == "ops@convergeai.com") |
                    (Staff.employee_id == "OPS001")
                )
            )
            existing_staff = result.scalar_one_or_none()

            if existing_staff:
                print(f"\n✅ Test operations staff user already exists:")
                print(f"   ID: {existing_staff.id}")
                print(f"   Employee ID: {existing_staff.employee_id}")
                print(f"   Email: {existing_staff.email}")
                print(f"   Mobile: {existing_staff.mobile}")
                print(f"   Name: {existing_staff.first_name} {existing_staff.last_name}")
                print(f"   Department: {existing_staff.department}")
                print(f"   Active: {existing_staff.is_active}")
                print(f"   Verified: {existing_staff.is_verified}")

                # Update password to known value
                print(f"\n🔄 Updating password to known value...")
                existing_staff.password_hash = hash_password("OpsPass123!")
                await db.commit()

                print(f"\n📝 Updated login credentials:")
                print(f"   Email: {existing_staff.email}")
                print(f"   Password: OpsPass123!")
                print(f"\n🔗 Test login at: http://localhost:5174/")
                return existing_staff
            
            # Get first available role (or create a basic one)
            result = await db.execute(select(Role).limit(1))
            role = result.scalar_one_or_none()
            
            if not role:
                # Create a basic role if none exists
                role = Role(
                    name="operations_staff",
                    display_name="Operations Staff",
                    description="Basic operations staff role",
                    level=3,
                    is_active=True
                )
                db.add(role)
                await db.flush()
                print(f"✅ Created basic role: {role.name}")
            
            # Create test staff user
            staff = Staff(
                employee_id="OPS001",
                role_id=role.id,
                email="ops@convergeai.com",
                mobile="+919876543210",
                password_hash=hash_password("OpsPass123!"),
                first_name="Operations",
                last_name="Staff",
                department="Operations",
                designation="Operations Manager",
                date_of_joining=date.today(),
                is_active=True,
                is_verified=True
            )
            
            db.add(staff)
            await db.commit()
            await db.refresh(staff)
            
            print(f"\n✅ Test operations staff user created successfully!")
            print(f"   ID: {staff.id}")
            print(f"   Employee ID: {staff.employee_id}")
            print(f"   Email: {staff.email}")
            print(f"   Mobile: {staff.mobile}")
            print(f"   Name: {staff.first_name} {staff.last_name}")
            print(f"   Department: {staff.department}")
            print(f"   Role ID: {staff.role_id}")
            print(f"   Active: {staff.is_active}")
            print(f"   Verified: {staff.is_verified}")
            
            print(f"\n📝 Login credentials for testing:")
            print(f"   Email: ops@convergeai.com")
            print(f"   Password: OpsPass123!")
            print(f"\n🔗 Test login at: http://localhost:5174/")
            
            return staff
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating test staff user: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(create_test_ops_user())
