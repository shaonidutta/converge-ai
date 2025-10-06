-- STAFF AND ROLE-BASED ACCESS CONTROL (RBAC) DESIGN
-- Separate staff/employees from customers with proper role management

-- ============================================================================
-- PROBLEM WITH CURRENT DESIGN
-- ============================================================================
-- ❌ users table mixes customers and ops staff
-- ❌ No clear role hierarchy
-- ❌ No granular permissions
-- ❌ Security concerns mixing customer and staff data
-- ❌ Different authentication needs for staff vs customers

-- ============================================================================
-- NEW DESIGN - STAFF AND RBAC
-- ============================================================================

-- 1. ROLES TABLE - Define all roles in the system
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    level INT NOT NULL DEFAULT 0,  -- Hierarchy level (higher = more authority)
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_level (level),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample roles
INSERT INTO roles (name, display_name, description, level) VALUES
('super_admin', 'Super Administrator', 'Full system access, can manage everything', 100),
('admin', 'Administrator', 'System administration, user management', 90),
('manager', 'Manager', 'Team management, reporting, analytics', 80),
('ops_lead', 'Operations Lead', 'Lead operations team, handle escalations', 70),
('ops_staff', 'Operations Staff', 'Handle customer queries, bookings, complaints', 60),
('support_staff', 'Support Staff', 'Customer support, basic operations', 50),
('finance_staff', 'Finance Staff', 'Handle payments, refunds, settlements', 60),
('quality_staff', 'Quality Assurance', 'Review service quality, provider ratings', 55);

-- 2. PERMISSIONS TABLE - Define all permissions
CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL,  -- bookings, users, providers, complaints, etc.
    action VARCHAR(50) NOT NULL,  -- create, read, update, delete, approve, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_module (module),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample permissions
INSERT INTO permissions (name, display_name, description, module, action) VALUES
-- User Management
('users.view', 'View Users', 'View customer list and details', 'users', 'read'),
('users.edit', 'Edit Users', 'Edit customer information', 'users', 'update'),
('users.delete', 'Delete Users', 'Delete/deactivate customers', 'users', 'delete'),

-- Booking Management
('bookings.view', 'View Bookings', 'View all bookings', 'bookings', 'read'),
('bookings.create', 'Create Bookings', 'Create bookings on behalf of customers', 'bookings', 'create'),
('bookings.edit', 'Edit Bookings', 'Modify booking details', 'bookings', 'update'),
('bookings.cancel', 'Cancel Bookings', 'Cancel bookings', 'bookings', 'delete'),
('bookings.assign', 'Assign Providers', 'Assign providers to bookings', 'bookings', 'assign'),

-- Provider Management
('providers.view', 'View Providers', 'View provider list and details', 'providers', 'read'),
('providers.create', 'Create Providers', 'Onboard new providers', 'providers', 'create'),
('providers.edit', 'Edit Providers', 'Edit provider information', 'providers', 'update'),
('providers.verify', 'Verify Providers', 'Verify provider documents', 'providers', 'approve'),
('providers.deactivate', 'Deactivate Providers', 'Deactivate providers', 'providers', 'delete'),

-- Complaint Management
('complaints.view', 'View Complaints', 'View all complaints', 'complaints', 'read'),
('complaints.assign', 'Assign Complaints', 'Assign complaints to staff', 'complaints', 'assign'),
('complaints.resolve', 'Resolve Complaints', 'Mark complaints as resolved', 'complaints', 'update'),
('complaints.escalate', 'Escalate Complaints', 'Escalate to higher authority', 'complaints', 'escalate'),

-- Payment Management
('payments.view', 'View Payments', 'View payment transactions', 'payments', 'read'),
('payments.refund', 'Process Refunds', 'Initiate refunds', 'payments', 'refund'),
('payments.settle', 'Settle Payments', 'Settle provider payments', 'payments', 'settle'),

-- Analytics & Reports
('analytics.view', 'View Analytics', 'Access analytics dashboard', 'analytics', 'read'),
('reports.generate', 'Generate Reports', 'Generate system reports', 'reports', 'create'),
('reports.export', 'Export Reports', 'Export reports to CSV/PDF', 'reports', 'export'),

-- System Administration
('staff.view', 'View Staff', 'View staff members', 'staff', 'read'),
('staff.create', 'Create Staff', 'Add new staff members', 'staff', 'create'),
('staff.edit', 'Edit Staff', 'Edit staff information', 'staff', 'update'),
('staff.delete', 'Delete Staff', 'Remove staff members', 'staff', 'delete'),
('roles.manage', 'Manage Roles', 'Create and edit roles', 'roles', 'manage'),
('permissions.manage', 'Manage Permissions', 'Assign permissions to roles', 'permissions', 'manage'),
('settings.manage', 'Manage Settings', 'Configure system settings', 'settings', 'manage');

-- 3. ROLE_PERMISSIONS TABLE - Map permissions to roles
CREATE TABLE role_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    INDEX idx_role (role_id),
    INDEX idx_permission (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. STAFF TABLE - Employees/Staff members
CREATE TABLE staff (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,  -- EMP001, EMP002, etc.
    role_id INT NOT NULL,
    
    -- Personal Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    last_login DATETIME,
    login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    
    -- Employment Details
    department VARCHAR(100),
    designation VARCHAR(100),
    reporting_to BIGINT,  -- FK to another staff member
    date_of_joining DATE,
    date_of_leaving DATE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (reporting_to) REFERENCES staff(id) ON DELETE SET NULL,
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_email (email),
    INDEX idx_mobile (mobile),
    INDEX idx_role (role_id),
    INDEX idx_active (is_active),
    INDEX idx_reporting_to (reporting_to)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. STAFF_SESSIONS TABLE - Track staff login sessions
CREATE TABLE staff_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    staff_id BIGINT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_at DATETIME,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    
    INDEX idx_staff (staff_id),
    INDEX idx_token (session_token),
    INDEX idx_active (is_active),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. STAFF_ACTIVITY_LOG TABLE - Audit trail for staff actions
CREATE TABLE staff_activity_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    staff_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),  -- booking, user, provider, etc.
    entity_id BIGINT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    
    INDEX idx_staff (staff_id),
    INDEX idx_action (action),
    INDEX idx_module (module),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- UPDATE EXISTING TABLES TO REFERENCE STAFF INSTEAD OF USERS
-- ============================================================================

-- Update priority_queue table
ALTER TABLE priority_queue 
    ADD COLUMN reviewed_by_staff_id BIGINT AFTER reviewed_by,
    ADD FOREIGN KEY (reviewed_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL;

-- Update complaints table
ALTER TABLE complaints
    ADD COLUMN assigned_to_staff_id BIGINT AFTER assigned_to,
    ADD COLUMN resolved_by_staff_id BIGINT AFTER resolved_by,
    ADD FOREIGN KEY (assigned_to_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
    ADD FOREIGN KEY (resolved_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL;

-- Update complaint_updates table
ALTER TABLE complaint_updates
    ADD COLUMN staff_id BIGINT AFTER user_id,
    ADD FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE;

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Staff with their roles and permissions
CREATE VIEW staff_with_permissions AS
SELECT 
    s.id,
    s.employee_id,
    s.first_name,
    s.last_name,
    s.email,
    s.mobile,
    r.name as role_name,
    r.display_name as role_display_name,
    r.level as role_level,
    GROUP_CONCAT(p.name) as permissions
FROM staff s
JOIN roles r ON s.role_id = r.id
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
WHERE s.is_active = TRUE
GROUP BY s.id, s.employee_id, s.first_name, s.last_name, s.email, s.mobile, 
         r.name, r.display_name, r.level;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Check if staff has specific permission
SELECT EXISTS(
    SELECT 1 
    FROM staff s
    JOIN roles r ON s.role_id = r.id
    JOIN role_permissions rp ON r.id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    WHERE s.id = 1 
    AND p.name = 'bookings.cancel'
) as has_permission;

-- Get all permissions for a staff member
SELECT p.name, p.display_name, p.module, p.action
FROM staff s
JOIN roles r ON s.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE s.id = 1;

-- Get staff hierarchy (reporting structure)
WITH RECURSIVE staff_hierarchy AS (
    SELECT id, employee_id, first_name, last_name, reporting_to, 0 as level
    FROM staff
    WHERE reporting_to IS NULL
    
    UNION ALL
    
    SELECT s.id, s.employee_id, s.first_name, s.last_name, s.reporting_to, sh.level + 1
    FROM staff s
    JOIN staff_hierarchy sh ON s.reporting_to = sh.id
)
SELECT * FROM staff_hierarchy ORDER BY level, employee_id;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

