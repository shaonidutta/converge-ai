-- ============================================================================
-- Migration: Add alerts, alert_rules, and alert_subscriptions tables
-- Purpose: Support alert system for operational notifications
-- Date: 2025-10-15
-- ============================================================================

-- ============================================================================
-- Table: alerts
-- Purpose: Store all system alerts for staff members
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(50) NOT NULL COMMENT 'Type: sla_breach, critical_complaint, high_workload, etc.',
    severity VARCHAR(20) NOT NULL COMMENT 'Severity: info, warning, critical',
    title VARCHAR(255) NOT NULL COMMENT 'Alert title',
    message TEXT NOT NULL COMMENT 'Alert message/description',
    resource_type VARCHAR(50) NULL COMMENT 'Related resource: complaint, booking, etc.',
    resource_id BIGINT NULL COMMENT 'ID of related resource',
    assigned_to_staff_id BIGINT NULL COMMENT 'Staff member assigned (NULL for broadcast)',
    is_read BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Whether alert has been read',
    is_dismissed BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Whether alert has been dismissed',
    alert_metadata JSON NULL COMMENT 'Additional alert metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    read_at TIMESTAMP NULL COMMENT 'When alert was read',
    dismissed_at TIMESTAMP NULL COMMENT 'When alert was dismissed',
    expires_at TIMESTAMP NULL COMMENT 'When alert expires',
    
    INDEX idx_staff_unread (assigned_to_staff_id, is_read, created_at),
    INDEX idx_type_severity (alert_type, severity, created_at),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_expires (expires_at),
    
    FOREIGN KEY (assigned_to_staff_id) REFERENCES staff(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: alert_rules
-- Purpose: Configurable alert rules for automatic alert generation
-- ============================================================================

CREATE TABLE IF NOT EXISTS alert_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_name VARCHAR(100) UNIQUE NOT NULL COMMENT 'Unique rule name',
    rule_type VARCHAR(50) NOT NULL COMMENT 'Type: sla, threshold, event',
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Whether rule is active',
    conditions JSON NOT NULL COMMENT 'Rule conditions (JSON)',
    alert_config JSON NOT NULL COMMENT 'Alert configuration (JSON)',
    created_by_staff_id BIGINT NULL COMMENT 'Staff who created the rule',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    INDEX idx_enabled (is_enabled),
    INDEX idx_rule_type (rule_type, is_enabled),
    
    FOREIGN KEY (created_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: alert_subscriptions
-- Purpose: Staff alert preferences and delivery channels
-- ============================================================================

CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT NOT NULL COMMENT 'Staff member',
    alert_type VARCHAR(50) NOT NULL COMMENT 'Alert type to subscribe to',
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Whether subscription is active',
    delivery_channels JSON NULL COMMENT 'Delivery channels: ["in_app", "email", "sms"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    UNIQUE KEY unique_subscription (staff_id, alert_type),
    INDEX idx_staff_enabled (staff_id, is_enabled),
    
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Insert default alert rules
-- ============================================================================

INSERT INTO alert_rules (rule_name, rule_type, is_enabled, conditions, alert_config) VALUES
(
    'sla_breach_critical',
    'sla',
    TRUE,
    JSON_OBJECT(
        'priority', 'CRITICAL',
        'buffer_hours', 1,
        'check_response', TRUE,
        'check_resolution', TRUE
    ),
    JSON_OBJECT(
        'alert_type', 'sla_breach',
        'severity', 'critical',
        'title_template', 'CRITICAL: SLA Breach for Complaint #{resource_id}',
        'message_template', 'Complaint #{resource_id} has breached SLA deadline. Immediate action required.',
        'assign_to_owner', TRUE,
        'broadcast_to_managers', TRUE
    )
),
(
    'sla_at_risk',
    'sla',
    TRUE,
    JSON_OBJECT(
        'buffer_hours', 1,
        'check_response', TRUE,
        'check_resolution', TRUE
    ),
    JSON_OBJECT(
        'alert_type', 'sla_at_risk',
        'severity', 'warning',
        'title_template', 'SLA At Risk: Complaint #{resource_id}',
        'message_template', 'Complaint #{resource_id} is approaching SLA deadline in less than 1 hour.',
        'assign_to_owner', TRUE
    )
),
(
    'critical_complaint_created',
    'event',
    TRUE,
    JSON_OBJECT(
        'event_type', 'complaint_created',
        'priority', 'CRITICAL'
    ),
    JSON_OBJECT(
        'alert_type', 'critical_complaint',
        'severity', 'critical',
        'title_template', 'CRITICAL Complaint Created: #{resource_id}',
        'message_template', 'A new CRITICAL priority complaint has been created. Immediate attention required.',
        'broadcast_to_all_ops', TRUE
    )
),
(
    'high_workload_warning',
    'threshold',
    TRUE,
    JSON_OBJECT(
        'metric', 'assigned_complaints',
        'threshold', 10,
        'operator', 'greater_than'
    ),
    JSON_OBJECT(
        'alert_type', 'high_workload',
        'severity', 'warning',
        'title_template', 'High Workload Alert',
        'message_template', 'You have {count} assigned complaints. Consider redistributing workload.',
        'assign_to_staff', TRUE
    )
);

-- ============================================================================
-- Verification
-- ============================================================================

SELECT 'alerts table created' as status, COUNT(*) as row_count FROM alerts;
SELECT 'alert_rules table created' as status, COUNT(*) as row_count FROM alert_rules;
SELECT 'alert_subscriptions table created' as status, COUNT(*) as row_count FROM alert_subscriptions;

