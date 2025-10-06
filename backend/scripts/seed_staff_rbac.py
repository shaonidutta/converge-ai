"""
Seed staff, roles, and permissions
Migrate ops staff from users table to staff table
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

print("="*80)
print("SEEDING STAFF, ROLES, AND PERMISSIONS")
print("="*80)

session = Session()

try:
    # Import models
    from backend.src.core.models import Role, Permission, RolePermission, Staff
    
    # Step 1: Create Roles
    print("\n1. Creating Roles...")
    roles_data = [
        {'name': 'super_admin', 'display_name': 'Super Administrator', 'description': 'Full system access, can manage everything', 'level': 100},
        {'name': 'admin', 'display_name': 'Administrator', 'description': 'System administration, user management', 'level': 90},
        {'name': 'manager', 'display_name': 'Manager', 'description': 'Team management, reporting, analytics', 'level': 80},
        {'name': 'ops_lead', 'display_name': 'Operations Lead', 'description': 'Lead operations team, handle escalations', 'level': 70},
        {'name': 'ops_staff', 'display_name': 'Operations Staff', 'description': 'Handle customer queries, bookings, complaints', 'level': 60},
        {'name': 'support_staff', 'display_name': 'Support Staff', 'description': 'Customer support, basic operations', 'level': 50},
        {'name': 'finance_staff', 'display_name': 'Finance Staff', 'description': 'Handle payments, refunds, settlements', 'level': 60},
        {'name': 'quality_staff', 'display_name': 'Quality Assurance', 'description': 'Review service quality, provider ratings', 'level': 55},
    ]
    
    roles = {}
    for role_data in roles_data:
        role = Role(**role_data)
        session.add(role)
        session.flush()
        roles[role_data['name']] = role
        print(f"   ✓ Created role: {role.display_name} (level {role.level})")
    
    session.commit()
    print(f"\n   Total roles created: {len(roles)}")
    
    # Step 2: Create Permissions
    print("\n2. Creating Permissions...")
    permissions_data = [
        # User Management
        {'name': 'users.view', 'display_name': 'View Users', 'description': 'View customer list and details', 'module': 'users', 'action': 'read'},
        {'name': 'users.edit', 'display_name': 'Edit Users', 'description': 'Edit customer information', 'module': 'users', 'action': 'update'},
        {'name': 'users.delete', 'display_name': 'Delete Users', 'description': 'Delete/deactivate customers', 'module': 'users', 'action': 'delete'},
        
        # Booking Management
        {'name': 'bookings.view', 'display_name': 'View Bookings', 'description': 'View all bookings', 'module': 'bookings', 'action': 'read'},
        {'name': 'bookings.create', 'display_name': 'Create Bookings', 'description': 'Create bookings on behalf of customers', 'module': 'bookings', 'action': 'create'},
        {'name': 'bookings.edit', 'display_name': 'Edit Bookings', 'description': 'Modify booking details', 'module': 'bookings', 'action': 'update'},
        {'name': 'bookings.cancel', 'display_name': 'Cancel Bookings', 'description': 'Cancel bookings', 'module': 'bookings', 'action': 'delete'},
        {'name': 'bookings.assign', 'display_name': 'Assign Providers', 'description': 'Assign providers to bookings', 'module': 'bookings', 'action': 'assign'},
        
        # Provider Management
        {'name': 'providers.view', 'display_name': 'View Providers', 'description': 'View provider list and details', 'module': 'providers', 'action': 'read'},
        {'name': 'providers.create', 'display_name': 'Create Providers', 'description': 'Onboard new providers', 'module': 'providers', 'action': 'create'},
        {'name': 'providers.edit', 'display_name': 'Edit Providers', 'description': 'Edit provider information', 'module': 'providers', 'action': 'update'},
        {'name': 'providers.verify', 'display_name': 'Verify Providers', 'description': 'Verify provider documents', 'module': 'providers', 'action': 'approve'},
        {'name': 'providers.deactivate', 'display_name': 'Deactivate Providers', 'description': 'Deactivate providers', 'module': 'providers', 'action': 'delete'},
        
        # Complaint Management
        {'name': 'complaints.view', 'display_name': 'View Complaints', 'description': 'View all complaints', 'module': 'complaints', 'action': 'read'},
        {'name': 'complaints.assign', 'display_name': 'Assign Complaints', 'description': 'Assign complaints to staff', 'module': 'complaints', 'action': 'assign'},
        {'name': 'complaints.resolve', 'display_name': 'Resolve Complaints', 'description': 'Mark complaints as resolved', 'module': 'complaints', 'action': 'update'},
        {'name': 'complaints.escalate', 'display_name': 'Escalate Complaints', 'description': 'Escalate to higher authority', 'module': 'complaints', 'action': 'escalate'},
        
        # Payment Management
        {'name': 'payments.view', 'display_name': 'View Payments', 'description': 'View payment transactions', 'module': 'payments', 'action': 'read'},
        {'name': 'payments.refund', 'display_name': 'Process Refunds', 'description': 'Initiate refunds', 'module': 'payments', 'action': 'refund'},
        {'name': 'payments.settle', 'display_name': 'Settle Payments', 'description': 'Settle provider payments', 'module': 'payments', 'action': 'settle'},
        
        # Analytics & Reports
        {'name': 'analytics.view', 'display_name': 'View Analytics', 'description': 'Access analytics dashboard', 'module': 'analytics', 'action': 'read'},
        {'name': 'reports.generate', 'display_name': 'Generate Reports', 'description': 'Generate system reports', 'module': 'reports', 'action': 'create'},
        {'name': 'reports.export', 'display_name': 'Export Reports', 'description': 'Export reports to CSV/PDF', 'module': 'reports', 'action': 'export'},
        
        # System Administration
        {'name': 'staff.view', 'display_name': 'View Staff', 'description': 'View staff members', 'module': 'staff', 'action': 'read'},
        {'name': 'staff.create', 'display_name': 'Create Staff', 'description': 'Add new staff members', 'module': 'staff', 'action': 'create'},
        {'name': 'staff.edit', 'display_name': 'Edit Staff', 'description': 'Edit staff information', 'module': 'staff', 'action': 'update'},
        {'name': 'staff.delete', 'display_name': 'Delete Staff', 'description': 'Remove staff members', 'module': 'staff', 'action': 'delete'},
        {'name': 'roles.manage', 'display_name': 'Manage Roles', 'description': 'Create and edit roles', 'module': 'roles', 'action': 'manage'},
        {'name': 'permissions.manage', 'display_name': 'Manage Permissions', 'description': 'Assign permissions to roles', 'module': 'permissions', 'action': 'manage'},
        {'name': 'settings.manage', 'display_name': 'Manage Settings', 'description': 'Configure system settings', 'module': 'settings', 'action': 'manage'},
    ]
    
    permissions = {}
    for perm_data in permissions_data:
        permission = Permission(**perm_data)
        session.add(permission)
        session.flush()
        permissions[perm_data['name']] = permission
    
    session.commit()
    print(f"   ✓ Created {len(permissions)} permissions")
    
    # Step 3: Assign Permissions to Roles
    print("\n3. Assigning Permissions to Roles...")
    
    # Super Admin - All permissions
    super_admin_perms = list(permissions.values())
    for perm in super_admin_perms:
        rp = RolePermission(role_id=roles['super_admin'].id, permission_id=perm.id)
        session.add(rp)
    print(f"   ✓ Super Admin: {len(super_admin_perms)} permissions")
    
    # Admin - Most permissions except system management
    admin_perms = [p for p in permissions.values() if not p.name.startswith(('roles.', 'permissions.'))]
    for perm in admin_perms:
        rp = RolePermission(role_id=roles['admin'].id, permission_id=perm.id)
        session.add(rp)
    print(f"   ✓ Admin: {len(admin_perms)} permissions")
    
    # Manager - View all, manage bookings, complaints, reports
    manager_perm_names = [
        'users.view', 'bookings.view', 'bookings.edit', 'bookings.assign', 'bookings.cancel',
        'providers.view', 'providers.edit', 'complaints.view', 'complaints.assign', 'complaints.resolve',
        'complaints.escalate', 'payments.view', 'analytics.view', 'reports.generate', 'reports.export',
        'staff.view'
    ]
    for perm_name in manager_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['manager'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Manager: {len(manager_perm_names)} permissions")
    
    # Ops Lead - Similar to manager but less admin access
    ops_lead_perm_names = [
        'users.view', 'bookings.view', 'bookings.edit', 'bookings.assign', 'bookings.cancel',
        'providers.view', 'providers.edit', 'complaints.view', 'complaints.assign', 'complaints.resolve',
        'complaints.escalate', 'payments.view', 'analytics.view'
    ]
    for perm_name in ops_lead_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['ops_lead'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Ops Lead: {len(ops_lead_perm_names)} permissions")
    
    # Ops Staff - Basic operations
    ops_staff_perm_names = [
        'users.view', 'bookings.view', 'bookings.edit', 'bookings.assign',
        'providers.view', 'complaints.view', 'complaints.assign', 'complaints.resolve',
        'payments.view'
    ]
    for perm_name in ops_staff_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['ops_staff'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Ops Staff: {len(ops_staff_perm_names)} permissions")
    
    # Support Staff - View and basic support
    support_staff_perm_names = [
        'users.view', 'bookings.view', 'providers.view', 'complaints.view', 'complaints.assign'
    ]
    for perm_name in support_staff_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['support_staff'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Support Staff: {len(support_staff_perm_names)} permissions")
    
    # Finance Staff - Payment related
    finance_staff_perm_names = [
        'bookings.view', 'payments.view', 'payments.refund', 'payments.settle',
        'analytics.view', 'reports.generate', 'reports.export'
    ]
    for perm_name in finance_staff_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['finance_staff'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Finance Staff: {len(finance_staff_perm_names)} permissions")
    
    # Quality Staff - Provider and service quality
    quality_staff_perm_names = [
        'providers.view', 'providers.edit', 'providers.verify', 'providers.deactivate',
        'bookings.view', 'complaints.view', 'analytics.view'
    ]
    for perm_name in quality_staff_perm_names:
        if perm_name in permissions:
            rp = RolePermission(role_id=roles['quality_staff'].id, permission_id=permissions[perm_name].id)
            session.add(rp)
    print(f"   ✓ Quality Staff: {len(quality_staff_perm_names)} permissions")
    
    session.commit()
    
    # Step 4: Create sample staff members
    print("\n4. Creating Sample Staff Members...")
    
    # Default password for all staff (should be changed on first login)
    default_password = "ConvergeAI@2025"
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    staff_data = [
        {'employee_id': 'EMP001', 'role': 'super_admin', 'first_name': 'Admin', 'last_name': 'User', 'email': 'admin@convergeai.com', 'mobile': '+919999999999', 'department': 'Administration', 'designation': 'Super Administrator'},
        {'employee_id': 'EMP002', 'role': 'manager', 'first_name': 'Rajesh', 'last_name': 'Kumar', 'email': 'rajesh.kumar@convergeai.com', 'mobile': '+919999999998', 'department': 'Operations', 'designation': 'Operations Manager'},
        {'employee_id': 'EMP003', 'role': 'ops_lead', 'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya.sharma@convergeai.com', 'mobile': '+919999999997', 'department': 'Operations', 'designation': 'Operations Lead'},
        {'employee_id': 'EMP004', 'role': 'ops_staff', 'first_name': 'Amit', 'last_name': 'Patel', 'email': 'amit.patel@convergeai.com', 'mobile': '+919999999996', 'department': 'Operations', 'designation': 'Operations Executive'},
        {'employee_id': 'EMP005', 'role': 'ops_staff', 'first_name': 'Sneha', 'last_name': 'Reddy', 'email': 'sneha.reddy@convergeai.com', 'mobile': '+919999999995', 'department': 'Operations', 'designation': 'Operations Executive'},
    ]
    
    for staff_info in staff_data:
        role_name = staff_info.pop('role')
        staff = Staff(
            **staff_info,
            role_id=roles[role_name].id,
            password_hash=password_hash,
            date_of_joining=date.today(),
            is_active=True,
            is_verified=True
        )
        session.add(staff)
        print(f"   ✓ Created staff: {staff.employee_id} - {staff.first_name} {staff.last_name} ({roles[role_name].display_name})")
    
    session.commit()
    
    print("\n" + "="*80)
    print("SEEDING COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"\nRoles: {len(roles)}")
    print(f"Permissions: {len(permissions)}")
    print(f"Staff Members: {len(staff_data)}")
    print(f"\nDefault Password for all staff: {default_password}")
    print("⚠️  Please change passwords on first login!")
    
except Exception as e:
    session.rollback()
    print(f"\n✗ Error during seeding: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()

