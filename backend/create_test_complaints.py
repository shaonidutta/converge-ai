#!/usr/bin/env python3
"""
Create test complaints for Phase 3 testing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.core.models import (
    User, Booking, Complaint, ComplaintUpdate, Staff,
    ComplaintStatus, ComplaintPriority, ComplaintType
)
from src.core.config import get_settings

async def create_test_complaints():
    """Create test complaints for Phase 3 testing"""
    print("=" * 80)
    print("Creating Test Complaints for Phase 3 Testing")
    print("=" * 80)

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Check if we have users and staff
            users_result = await session.execute(select(User).limit(5))
            users = users_result.scalars().all()
            
            staff_result = await session.execute(select(Staff).limit(3))
            staff = staff_result.scalars().all()
            
            if not users:
                print("❌ No users found. Please create some users first.")
                return False
                
            if not staff:
                print("❌ No staff found. Please create some staff first.")
                return False

            print(f"✅ Found {len(users)} users and {len(staff)} staff members")

            # Create test complaints
            test_complaints = [
                {
                    "user_id": users[0].id,
                    "complaint_type": ComplaintType.SERVICE_QUALITY,
                    "subject": "Poor service quality during AC repair",
                    "description": "The technician arrived late and did not properly fix the AC unit. It's still not cooling properly.",
                    "priority": ComplaintPriority.HIGH,
                    "status": ComplaintStatus.OPEN
                },
                {
                    "user_id": users[1].id if len(users) > 1 else users[0].id,
                    "complaint_type": ComplaintType.BILLING,
                    "subject": "Incorrect billing amount charged",
                    "description": "I was charged ₹2500 for plumbing service but the quote was ₹1800. Please review the billing.",
                    "priority": ComplaintPriority.MEDIUM,
                    "status": ComplaintStatus.IN_PROGRESS,
                    "assigned_to_staff_id": staff[0].id,
                    "assigned_at": datetime.now(timezone.utc) - timedelta(hours=2)
                },
                {
                    "user_id": users[2].id if len(users) > 2 else users[0].id,
                    "complaint_type": ComplaintType.NO_SHOW,
                    "subject": "Technician did not show up for scheduled appointment",
                    "description": "I had a scheduled electrical work appointment today at 2 PM but no one showed up. Very disappointed.",
                    "priority": ComplaintPriority.CRITICAL,
                    "status": ComplaintStatus.ESCALATED,
                    "assigned_to_staff_id": staff[1].id if len(staff) > 1 else staff[0].id,
                    "assigned_at": datetime.now(timezone.utc) - timedelta(hours=6)
                },
                {
                    "user_id": users[3].id if len(users) > 3 else users[0].id,
                    "complaint_type": ComplaintType.DAMAGE,
                    "subject": "Property damage during carpentry work",
                    "description": "The carpenter damaged my wall while installing shelves. There's a big hole that needs repair.",
                    "priority": ComplaintPriority.HIGH,
                    "status": ComplaintStatus.RESOLVED,
                    "assigned_to_staff_id": staff[0].id,
                    "assigned_at": datetime.now(timezone.utc) - timedelta(days=2),
                    "resolved_at": datetime.now(timezone.utc) - timedelta(hours=12),
                    "resolved_by_staff_id": staff[0].id,
                    "resolution": "Arranged for wall repair at no additional cost. Customer satisfied with resolution."
                },
                {
                    "user_id": users[4].id if len(users) > 4 else users[0].id,
                    "complaint_type": ComplaintType.OTHER,
                    "subject": "Unprofessional behavior from service provider",
                    "description": "The service provider was rude and unprofessional. Made inappropriate comments during the service.",
                    "priority": ComplaintPriority.MEDIUM,
                    "status": ComplaintStatus.OPEN
                }
            ]

            created_complaints = []
            for complaint_data in test_complaints:
                # Set timestamps
                created_at = datetime.now(timezone.utc) - timedelta(
                    hours=complaint_data.get('hours_ago', 0),
                    days=complaint_data.get('days_ago', 0)
                )
                
                # Calculate SLA due dates
                response_due_at = created_at + timedelta(hours=4)  # 4 hours for response
                resolution_due_at = created_at + timedelta(hours=48)  # 48 hours for resolution
                
                complaint = Complaint(
                    user_id=complaint_data["user_id"],
                    complaint_type=complaint_data["complaint_type"],
                    subject=complaint_data["subject"],
                    description=complaint_data["description"],
                    priority=complaint_data["priority"],
                    status=complaint_data["status"],
                    assigned_to_staff_id=complaint_data.get("assigned_to_staff_id"),
                    assigned_at=complaint_data.get("assigned_at"),
                    resolved_at=complaint_data.get("resolved_at"),
                    resolved_by_staff_id=complaint_data.get("resolved_by_staff_id"),
                    resolution=complaint_data.get("resolution"),
                    created_at=created_at,
                    updated_at=created_at,
                    response_due_at=response_due_at,
                    resolution_due_at=resolution_due_at
                )
                
                session.add(complaint)
                created_complaints.append(complaint)

            # Commit complaints
            await session.commit()
            
            # Refresh to get IDs
            for complaint in created_complaints:
                await session.refresh(complaint)

            print(f"✅ Created {len(created_complaints)} test complaints")

            # Add some updates to complaints
            updates_data = [
                {
                    "complaint_id": created_complaints[1].id,  # In progress complaint
                    "staff_id": staff[0].id,
                    "comment": "Investigating the billing discrepancy. Checking with accounts team.",
                    "is_internal": True
                },
                {
                    "complaint_id": created_complaints[1].id,
                    "staff_id": staff[0].id,
                    "comment": "We have reviewed your billing and found an error. A refund of ₹700 will be processed within 3-5 business days.",
                    "is_internal": False
                },
                {
                    "complaint_id": created_complaints[2].id,  # Escalated complaint
                    "staff_id": staff[1].id if len(staff) > 1 else staff[0].id,
                    "comment": "Escalated to senior management. Immediate action required.",
                    "is_internal": True
                }
            ]

            for update_data in updates_data:
                update = ComplaintUpdate(
                    complaint_id=update_data["complaint_id"],
                    user_id=created_complaints[0].user_id,  # Use first user
                    staff_id=update_data["staff_id"],
                    comment=update_data["comment"],
                    is_internal=update_data["is_internal"],
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=30)
                )
                session.add(update)

            await session.commit()
            print(f"✅ Added {len(updates_data)} complaint updates")

            print("\n" + "=" * 80)
            print("✅ Test complaints created successfully!")
            print("=" * 80)
            
            # Show summary
            print(f"\n📊 Summary:")
            print(f"  • Total complaints: {len(created_complaints)}")
            print(f"  • Open: {sum(1 for c in created_complaints if c.status == ComplaintStatus.OPEN)}")
            print(f"  • In Progress: {sum(1 for c in created_complaints if c.status == ComplaintStatus.IN_PROGRESS)}")
            print(f"  • Escalated: {sum(1 for c in created_complaints if c.status == ComplaintStatus.ESCALATED)}")
            print(f"  • Resolved: {sum(1 for c in created_complaints if c.status == ComplaintStatus.RESOLVED)}")
            print(f"  • Total updates: {len(updates_data)}")

            return True

    except Exception as e:
        print(f"\n❌ Error creating test complaints: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(create_test_complaints())
    sys.exit(0 if success else 1)
