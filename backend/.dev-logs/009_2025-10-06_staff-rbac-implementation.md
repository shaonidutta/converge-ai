# Staff and RBAC Implementation

**Date:** 2025-10-06  
**Author:** Augment Agent  
**Status:** ✅ COMPLETE

---

## Problem Statement

The original database design had ops staff and admins mixed with customers in the `users` table. This violated separation of concerns and created several issues:

1. **Security Concerns:** Staff and customers sharing the same authentication table
2. **No Access Control:** No way to define what actions staff can perform
3. **Audit Trail:** No tracking of staff actions
4. **Scalability:** Difficult to add new staff roles or permissions

---

## Solution Overview

Implemented a comprehensive **Staff and RBAC (Role-Based Access Control)** system with:

✅ **Separate staff table** for employees  
✅ **Hierarchical role system** with 8 predefined roles  
✅ **Granular permissions** across 10 modules  
✅ **Session management** with expiry tracking  
✅ **Activity logging** for audit trail  
✅ **Foreign key relationships** to existing tables  

---

## Database Schema

### New Tables

#### 1. `roles` - Role Definitions

```sql
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,           -- super_admin, admin, manager, etc.
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    level INT NOT NULL DEFAULT 0,               -- Hierarchy level (100=highest)
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role_name (name),
    INDEX idx_role_level (level),
    INDEX idx_role_active (is_active)
);
```

**Predefined Roles:**
- `super_admin` (level 100) - Full system access
- `admin` (level 90) - System administration
- `manager` (level 80) - Team management, reporting
- `ops_lead` (level 70) - Lead operations team
- `ops_staff` (level 60) - Handle customer queries
- `support_staff` (level 50) - Basic support
- `finance_staff` (level 60) - Payment operations
- `quality_staff` (level 55) - Quality assurance

#### 2. `permissions` - Granular Permissions

```sql
CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,          -- users.view, bookings.create, etc.
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL,                -- users, bookings, providers, etc.
    action VARCHAR(50) NOT NULL,                -- create, read, update, delete, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_permission_name (name),
    INDEX idx_permission_module (module),
    INDEX idx_permission_action (action)
);
```

**Permission Modules:**
- `users` - Customer management
- `bookings` - Booking operations
- `providers` - Provider management
- `complaints` - Complaint handling
- `payments` - Payment operations
- `analytics` - Analytics dashboard
- `reports` - Report generation
- `staff` - Staff management
- `roles` - Role management
- `permissions` - Permission management
- `settings` - System settings

**Permission Actions:**
- `create`, `read`, `update`, `delete`
- `assign`, `approve`, `verify`, `escalate`
- `refund`, `settle`, `export`, `manage`

#### 3. `role_permissions` - Junction Table

```sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    INDEX idx_rp_role (role_id),
    INDEX idx_rp_permission (permission_id)
);
```

#### 4. `staff` - Employee/Staff Members

```sql
CREATE TABLE staff (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(50) UNIQUE NOT NULL,    -- EMP001, EMP002, etc.
    role_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login DATETIME,
    login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    department VARCHAR(100),
    designation VARCHAR(100),
    reporting_to BIGINT,                        -- Self-referential FK
    date_of_joining DATE,
    date_of_leaving DATE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (reporting_to) REFERENCES staff(id) ON DELETE SET NULL,
    INDEX idx_staff_employee_id (employee_id),
    INDEX idx_staff_email (email),
    INDEX idx_staff_mobile (mobile),
    INDEX idx_staff_role (role_id),
    INDEX idx_staff_active (is_active),
    INDEX idx_staff_reporting (reporting_to)
);
```

#### 5. `staff_sessions` - Session Tracking

```sql
CREATE TABLE staff_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_at DATETIME,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    INDEX idx_session_staff (staff_id),
    INDEX idx_session_token (session_token),
    INDEX idx_session_active (is_active),
    INDEX idx_session_expires (expires_at)
);
```

#### 6. `staff_activity_log` - Audit Trail

```sql
CREATE TABLE staff_activity_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,               -- login, create_booking, resolve_complaint, etc.
    module VARCHAR(50) NOT NULL,                -- bookings, complaints, providers, etc.
    entity_type VARCHAR(50),                    -- booking, complaint, provider, etc.
    entity_id BIGINT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    INDEX idx_activity_staff (staff_id),
    INDEX idx_activity_action (action),
    INDEX idx_activity_module (module),
    INDEX idx_activity_entity (entity_type, entity_id),
    INDEX idx_activity_created (created_at)
);
```

### Updated Tables

#### `priority_queue` - Added Staff FK

```sql
ALTER TABLE priority_queue
ADD COLUMN reviewed_by_staff_id BIGINT,
ADD FOREIGN KEY (reviewed_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL;

-- Old column: reviewed_by (references users.id) - DEPRECATED
```

#### `complaints` - Added Staff FKs

```sql
ALTER TABLE complaints
ADD COLUMN assigned_to_staff_id BIGINT,
ADD COLUMN resolved_by_staff_id BIGINT,
ADD FOREIGN KEY (assigned_to_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
ADD FOREIGN KEY (resolved_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL;

-- Old columns: assigned_to, resolved_by (reference users.id) - DEPRECATED
```

#### `complaint_updates` - Added Staff FK

```sql
ALTER TABLE complaint_updates
ADD COLUMN staff_id BIGINT,
ADD FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE;

-- If update is from staff, staff_id is set; if from customer, user_id is set
```

---

## SQLAlchemy Models

### Role Model

```python
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    staff_members = relationship('Staff', back_populates='role')
    permissions = relationship('Permission', secondary='role_permissions', viewonly=True)
```

### Permission Model

```python
class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(150), nullable=False)
    module = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    
    # Relationships
    roles = relationship('Role', secondary='role_permissions', viewonly=True)
```

### Staff Model

```python
class Staff(Base):
    __tablename__ = 'staff'
    
    id = Column(BigInteger, primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationships
    role = relationship('Role', back_populates='staff_members')
    sessions = relationship('StaffSession', back_populates='staff')
    activity_logs = relationship('StaffActivityLog', back_populates='staff')
    
    # Permission checking methods
    def has_permission(self, permission_name: str) -> bool:
        return any(p.name == permission_name for p in self.role.permissions)
    
    def has_any_permission(self, permission_names: list) -> bool:
        staff_permissions = {p.name for p in self.role.permissions}
        return bool(staff_permissions.intersection(set(permission_names)))
    
    def has_all_permissions(self, permission_names: list) -> bool:
        staff_permissions = {p.name for p in self.role.permissions}
        return set(permission_names).issubset(staff_permissions)
```

---

## Usage Examples

### 1. Check Staff Permission

```python
# Get staff member
staff = session.query(Staff).filter_by(employee_id='EMP004').first()

# Check single permission
if staff.has_permission('bookings.create'):
    # Allow booking creation
    pass

# Check any of multiple permissions
if staff.has_any_permission(['bookings.edit', 'bookings.cancel']):
    # Allow booking modification
    pass

# Check all permissions
if staff.has_all_permissions(['complaints.view', 'complaints.assign', 'complaints.resolve']):
    # Allow full complaint management
    pass
```

### 2. Get Staff by Role

```python
# Get all ops staff
ops_staff = session.query(Staff).join(Role).filter(Role.name == 'ops_staff').all()

# Get staff with level >= 70 (ops_lead and above)
senior_staff = session.query(Staff).join(Role).filter(Role.level >= 70).all()
```

### 3. Log Staff Activity

```python
# Create activity log
activity = StaffActivityLog(
    staff_id=staff.id,
    action='resolve_complaint',
    module='complaints',
    entity_type='complaint',
    entity_id=complaint.id,
    description=f'Resolved complaint #{complaint.id}',
    ip_address='192.168.1.1'
)
session.add(activity)
session.commit()
```

### 4. Assign Complaint to Staff

```python
# Assign complaint to staff member
complaint.assigned_to_staff_id = staff.id
complaint.assigned_at = datetime.now(timezone.utc)
complaint.status = ComplaintStatus.IN_PROGRESS
session.commit()
```

---

## Sample Data

### Staff Members Created

| Employee ID | Name | Role | Email | Department |
|-------------|------|------|-------|------------|
| EMP001 | Admin User | Super Administrator | admin@convergeai.com | Administration |
| EMP002 | Rajesh Kumar | Manager | rajesh.kumar@convergeai.com | Operations |
| EMP003 | Priya Sharma | Operations Lead | priya.sharma@convergeai.com | Operations |
| EMP004 | Amit Patel | Operations Staff | amit.patel@convergeai.com | Operations |
| EMP005 | Sneha Reddy | Operations Staff | sneha.reddy@convergeai.com | Operations |

**Default Password:** `ConvergeAI@2025`  
⚠️ **Must be changed on first login!**

---

## Files Created/Modified

### New Files
- `backend/src/core/models/role.py` - Role, Permission, RolePermission models
- `backend/src/core/models/staff.py` - Staff, StaffSession, StaffActivityLog models
- `backend/alembic/versions/5ea86f4d316b_add_staff_and_rbac_tables.py` - Migration
- `backend/scripts/seed_staff_rbac.py` - Seed script
- `database/schema_staff_rbac.sql` - SQL reference

### Modified Files
- `backend/src/core/models/__init__.py` - Export new models
- `backend/src/core/models/priority_queue.py` - Add staff FK
- `backend/src/core/models/complaint.py` - Add staff FKs
- `backend/src/core/models/pincode.py` - Fix ForeignKey imports

---

## Next Steps

1. **Update seed_database.py** to use staff instead of ops users
2. **Create authentication endpoints** for staff login
3. **Implement permission middleware** for API routes
4. **Add staff management UI** in admin panel
5. **Create audit log viewer** for compliance

---

## Benefits

✅ **Security:** Separate authentication for staff and customers  
✅ **Access Control:** Granular permissions per role  
✅ **Audit Trail:** Complete activity logging  
✅ **Scalability:** Easy to add new roles/permissions  
✅ **Compliance:** Track all staff actions  
✅ **Flexibility:** Hierarchical role system  

---

**Status:** ✅ COMPLETE

