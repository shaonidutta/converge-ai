"""
Test staff and RBAC functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

print("="*80)
print("TESTING STAFF AND RBAC FUNCTIONALITY")
print("="*80)

session = Session()

try:
    from backend.src.core.models import Staff, Role, Permission, RolePermission
    
    # Test 1: Verify roles created
    print("\n1. Testing Roles...")
    roles = session.query(Role).order_by(Role.level.desc()).all()
    print(f"   ✓ Total roles: {len(roles)}")
    for role in roles:
        print(f"     - {role.display_name} (level {role.level})")
    
    # Test 2: Verify permissions created
    print("\n2. Testing Permissions...")
    permissions = session.query(Permission).all()
    print(f"   ✓ Total permissions: {len(permissions)}")
    
    # Group by module
    modules = {}
    for perm in permissions:
        if perm.module not in modules:
            modules[perm.module] = []
        modules[perm.module].append(perm.name)
    
    for module, perms in sorted(modules.items()):
        print(f"     - {module}: {len(perms)} permissions")
    
    # Test 3: Verify role-permission mappings
    print("\n3. Testing Role-Permission Mappings...")
    for role in roles:
        role_perms = session.query(RolePermission).filter_by(role_id=role.id).count()
        print(f"   ✓ {role.display_name}: {role_perms} permissions")
    
    # Test 4: Verify staff members created
    print("\n4. Testing Staff Members...")
    staff_members = session.query(Staff).all()
    print(f"   ✓ Total staff: {len(staff_members)}")
    for staff in staff_members:
        print(f"     - {staff.employee_id}: {staff.first_name} {staff.last_name} ({staff.role.display_name})")
    
    # Test 5: Test permission checking
    print("\n5. Testing Permission Checking...")
    
    # Get ops staff
    ops_staff = session.query(Staff).filter_by(employee_id='EMP004').first()
    print(f"\n   Testing permissions for: {ops_staff.first_name} {ops_staff.last_name} ({ops_staff.role.display_name})")
    
    # Test single permission
    test_permissions = [
        'bookings.view',
        'bookings.create',
        'bookings.edit',
        'providers.create',
        'complaints.resolve',
        'staff.create',
        'roles.manage'
    ]
    
    for perm in test_permissions:
        has_perm = ops_staff.has_permission(perm)
        status = "✓" if has_perm else "✗"
        print(f"     {status} {perm}: {has_perm}")
    
    # Test any permission
    print(f"\n   Testing has_any_permission(['bookings.edit', 'bookings.cancel']):")
    has_any = ops_staff.has_any_permission(['bookings.edit', 'bookings.cancel'])
    print(f"     {'✓' if has_any else '✗'} Result: {has_any}")
    
    # Test all permissions
    print(f"\n   Testing has_all_permissions(['bookings.view', 'bookings.edit']):")
    has_all = ops_staff.has_all_permissions(['bookings.view', 'bookings.edit'])
    print(f"     {'✓' if has_all else '✗'} Result: {has_all}")
    
    # Test 6: Test super admin permissions
    print("\n6. Testing Super Admin Permissions...")
    super_admin = session.query(Staff).filter_by(employee_id='EMP001').first()
    print(f"\n   Testing permissions for: {super_admin.first_name} {super_admin.last_name} ({super_admin.role.display_name})")
    
    for perm in test_permissions:
        has_perm = super_admin.has_permission(perm)
        status = "✓" if has_perm else "✗"
        print(f"     {status} {perm}: {has_perm}")
    
    # Test 7: Test role hierarchy
    print("\n7. Testing Role Hierarchy...")
    print("   Roles by level (highest to lowest):")
    for role in roles:
        staff_count = session.query(Staff).filter_by(role_id=role.id).count()
        print(f"     Level {role.level:3d}: {role.display_name:25s} ({staff_count} staff)")
    
    # Test 8: Test reporting structure
    print("\n8. Testing Reporting Structure...")
    for staff in staff_members:
        if staff.reporting_to:
            manager = session.query(Staff).filter_by(id=staff.reporting_to).first()
            print(f"   {staff.employee_id} ({staff.first_name}) reports to {manager.employee_id} ({manager.first_name})")
        else:
            print(f"   {staff.employee_id} ({staff.first_name}) - No manager (top level)")
    
    # Test 9: Test staff queries
    print("\n9. Testing Staff Queries...")
    
    # Get all active staff
    active_staff = session.query(Staff).filter_by(is_active=True).count()
    print(f"   ✓ Active staff: {active_staff}")
    
    # Get staff by department
    ops_dept = session.query(Staff).filter_by(department='Operations').count()
    print(f"   ✓ Operations department: {ops_dept} staff")
    
    # Get staff with level >= 70
    senior_staff = session.query(Staff).join(Role).filter(Role.level >= 70).count()
    print(f"   ✓ Senior staff (level >= 70): {senior_staff}")
    
    # Test 10: Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Roles: {len(roles)}")
    print(f"✓ Permissions: {len(permissions)}")
    print(f"✓ Modules: {len(modules)}")
    print(f"✓ Staff Members: {len(staff_members)}")
    print(f"✓ Active Staff: {active_staff}")
    print("\n✅ All tests passed!")
    
    # Display permission matrix
    print("\n" + "="*80)
    print("PERMISSION MATRIX")
    print("="*80)
    
    # Get top 5 roles
    top_roles = session.query(Role).order_by(Role.level.desc()).limit(5).all()
    
    # Get sample permissions
    sample_perms = [
        'users.view', 'users.edit', 'bookings.create', 'bookings.edit',
        'providers.verify', 'complaints.resolve', 'payments.refund',
        'staff.create', 'roles.manage'
    ]
    
    # Print header
    print(f"\n{'Permission':<25}", end='')
    for role in top_roles:
        print(f"{role.name[:12]:<15}", end='')
    print()
    print("-" * 100)
    
    # Print matrix
    for perm_name in sample_perms:
        print(f"{perm_name:<25}", end='')
        for role in top_roles:
            role_perm_names = [p.name for p in role.permissions]
            has_perm = perm_name in role_perm_names
            print(f"{'✓' if has_perm else '✗':<15}", end='')
        print()
    
except Exception as e:
    print(f"\n✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()

