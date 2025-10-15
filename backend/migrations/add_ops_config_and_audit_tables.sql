-- Migration: Add ops_config and ops_audit_log tables
-- Purpose: Support runtime configuration and audit logging for ops features
-- Date: 2025-10-15

-- ============================================================================
-- Table: ops_config
-- Purpose: Runtime configuration for operational features (feature flags)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default configurations
INSERT INTO ops_config (config_key, config_value, description) VALUES
('DEFAULT_STATUS_FILTER', 'pending', 'Default status filter for ops endpoints (pending/reviewed/all)'),
('SLA_BUFFER_HOURS', '1', 'Hours before SLA breach to flag as at-risk'),
('MAX_EXPAND_PER_HOUR', '100', 'Max full expand requests per staff per hour'),
('ENABLE_AUTO_ENRICHMENT', 'true', 'Enable automatic enrichment of results')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);

-- ============================================================================
-- Table: ops_audit_log
-- Purpose: Audit trail for ops operations and PII access
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops_audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    pii_accessed BOOLEAN DEFAULT FALSE,
    request_metadata JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_staff_action (staff_id, action, created_at),
    INDEX idx_pii_access (pii_accessed, created_at),
    INDEX idx_resource (resource_type, resource_id),
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Performance Indexes (Optional but Recommended)
-- Purpose: Optimize priority queue queries
-- ============================================================================

-- Index for ops priority queue view
CREATE INDEX IF NOT EXISTS idx_priority_queue_ops_view 
ON priority_queue(is_reviewed, priority_score DESC, created_at DESC);

-- Index for pending bookings (ops view)
CREATE INDEX IF NOT EXISTS idx_bookings_pending_ops 
ON bookings(status, payment_status, created_at DESC);

-- Index for complaints with SLA tracking (ops view)
CREATE INDEX IF NOT EXISTS idx_complaints_sla_ops 
ON complaints(status, priority, response_due_at, resolution_due_at);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify tables created
SELECT 
    TABLE_NAME, 
    TABLE_ROWS, 
    CREATE_TIME 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME IN ('ops_config', 'ops_audit_log');

-- Verify default configs inserted
SELECT * FROM ops_config;

-- Verify indexes created
SELECT 
    TABLE_NAME, 
    INDEX_NAME, 
    COLUMN_NAME 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME IN ('ops_config', 'ops_audit_log', 'priority_queue', 'bookings', 'complaints')
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

