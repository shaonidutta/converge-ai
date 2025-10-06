-- ConvergeAI - Schema Additions (Optional Tables)
-- These tables address gaps identified in validation analysis
-- Add these based on priority and requirements

-- =============================================================================
-- PRIORITY 1: CRITICAL - Add Before Production
-- =============================================================================

-- 1. Complaints Table
-- Purpose: Dedicated complaint management and lifecycle tracking
-- Impact: HIGH - Essential for customer support workflow
CREATE TABLE complaints (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    
    -- References
    booking_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED NOT NULL,
    session_id VARCHAR(100),
    
    -- Complaint Details
    complaint_type ENUM(
        'service_quality', 
        'provider_behavior', 
        'billing', 
        'delay', 
        'cancellation_issue',
        'refund_issue',
        'other'
    ) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Priority & Status
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'resolved', 'closed', 'escalated') DEFAULT 'open',
    
    -- Assignment
    assigned_to BIGINT UNSIGNED,
    assigned_at DATETIME,
    
    -- Resolution
    resolution TEXT,
    resolved_at DATETIME,
    resolved_by BIGINT UNSIGNED,
    
    -- SLA Tracking
    response_due_at DATETIME,
    resolution_due_at DATETIME,
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_user (user_id),
    INDEX idx_booking (booking_id),
    INDEX idx_assigned (assigned_to, status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Complaint Comments/Updates
CREATE TABLE complaint_updates (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    complaint_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    comment TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_complaint (complaint_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- PRIORITY 2: RECOMMENDED - Add in Phase 2
-- =============================================================================

-- 2. Reschedule History Table
-- Purpose: Track booking reschedule history and enforce limits
-- Impact: MEDIUM - Better audit trail and limit enforcement
CREATE TABLE reschedule_history (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    booking_item_id BIGINT UNSIGNED NOT NULL,
    
    -- Old Schedule
    old_scheduled_date DATE NOT NULL,
    old_scheduled_time_from TIME NOT NULL,
    old_scheduled_time_to TIME NOT NULL,
    
    -- New Schedule
    new_scheduled_date DATE NOT NULL,
    new_scheduled_time_from TIME NOT NULL,
    new_scheduled_time_to TIME NOT NULL,
    
    -- Reschedule Details
    reason TEXT,
    rescheduled_by ENUM('customer', 'provider', 'admin') NOT NULL,
    reschedule_charge DECIMAL(10,2) DEFAULT 0.00,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (booking_item_id) REFERENCES booking_items(id) ON DELETE CASCADE,
    INDEX idx_booking_item (booking_item_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add reschedule count to booking_items
ALTER TABLE booking_items 
ADD COLUMN reschedule_count INT DEFAULT 0 AFTER status;

-- 3. Refunds Table
-- Purpose: Detailed refund workflow tracking
-- Impact: MEDIUM - Better refund management
CREATE TABLE refunds (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    
    -- References
    booking_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Refund Details
    refund_amount DECIMAL(10,2) NOT NULL,
    refund_reason ENUM(
        'cancellation',
        'service_not_provided',
        'poor_quality',
        'billing_error',
        'other'
    ) NOT NULL,
    refund_description TEXT,
    
    -- Refund Method
    refund_method ENUM('original_payment', 'wallet', 'bank_transfer') DEFAULT 'original_payment',
    refund_destination VARCHAR(255),
    
    -- Status & Tracking
    status ENUM('pending', 'approved', 'processing', 'completed', 'failed', 'rejected') DEFAULT 'pending',
    refund_transaction_id VARCHAR(255),
    
    -- Approval
    approved_by BIGINT UNSIGNED,
    approved_at DATETIME,
    
    -- Processing
    processed_at DATETIME,
    completed_at DATETIME,
    
    -- Failure
    failure_reason TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_booking (booking_id),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Wallet Transactions Table
-- Purpose: Audit trail for wallet operations
-- Impact: LOW - Can track in application logs
CREATE TABLE wallet_transactions (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Transaction Details
    transaction_type ENUM(
        'credit',           -- Money added
        'debit',            -- Money deducted
        'refund',           -- Refund credited
        'referral_bonus',   -- Referral reward
        'cashback',         -- Cashback
        'adjustment'        -- Manual adjustment
    ) NOT NULL,
    
    amount DECIMAL(10,2) NOT NULL,
    balance_before DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    
    -- References
    booking_id BIGINT UNSIGNED,
    refund_id BIGINT UNSIGNED,
    reference_id VARCHAR(100),
    
    -- Description
    description VARCHAR(255),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
    FOREIGN KEY (refund_id) REFERENCES refunds(id) ON DELETE SET NULL,
    
    INDEX idx_user (user_id),
    INDEX idx_type (transaction_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- PRIORITY 3: OPTIONAL - Future Enhancement
-- =============================================================================

-- 5. Provider Ratings Table
-- Purpose: Detailed rating and review tracking
-- Impact: LOW - Can calculate avg_rating from this
CREATE TABLE provider_ratings (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    
    booking_item_id BIGINT UNSIGNED NOT NULL,
    provider_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Rating
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    review TEXT,
    
    -- Rating Categories
    punctuality_rating INT CHECK (punctuality_rating >= 1 AND punctuality_rating <= 5),
    quality_rating INT CHECK (quality_rating >= 1 AND quality_rating <= 5),
    behavior_rating INT CHECK (behavior_rating >= 1 AND behavior_rating <= 5),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (booking_item_id) REFERENCES booking_items(id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_provider (provider_id),
    INDEX idx_user (user_id),
    INDEX idx_rating (rating),
    UNIQUE KEY unique_rating (booking_item_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Notifications Table
-- Purpose: Track all notifications sent to users
-- Impact: LOW - Can use external notification service
CREATE TABLE notifications (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Notification Details
    type ENUM(
        'booking_confirmed',
        'booking_cancelled',
        'provider_assigned',
        'service_started',
        'service_completed',
        'payment_received',
        'refund_processed',
        'complaint_update',
        'promotional'
    ) NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Delivery
    channel ENUM('push', 'sms', 'email', 'whatsapp') NOT NULL,
    status ENUM('pending', 'sent', 'delivered', 'failed') DEFAULT 'pending',
    
    -- References
    booking_id BIGINT UNSIGNED,
    complaint_id BIGINT UNSIGNED,
    
    -- Tracking
    sent_at DATETIME,
    delivered_at DATETIME,
    read_at DATETIME,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE SET NULL,
    
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- VIEWS FOR NEW TABLES
-- =============================================================================

-- Open complaints with user details
CREATE OR REPLACE VIEW v_open_complaints AS
SELECT 
    c.id,
    c.complaint_type,
    c.subject,
    c.priority,
    c.status,
    u.mobile AS user_mobile,
    u.first_name AS user_name,
    b.order_id,
    assigned.first_name AS assigned_to_name,
    c.created_at,
    TIMESTAMPDIFF(HOUR, c.created_at, NOW()) AS hours_open
FROM complaints c
JOIN users u ON c.user_id = u.id
LEFT JOIN bookings b ON c.booking_id = b.id
LEFT JOIN users assigned ON c.assigned_to = assigned.id
WHERE c.status IN ('open', 'in_progress')
ORDER BY c.priority DESC, c.created_at ASC;

-- Pending refunds
CREATE OR REPLACE VIEW v_pending_refunds AS
SELECT 
    r.id,
    r.refund_amount,
    r.status,
    u.mobile AS user_mobile,
    u.first_name AS user_name,
    b.order_id,
    r.created_at,
    TIMESTAMPDIFF(DAY, r.created_at, NOW()) AS days_pending
FROM refunds r
JOIN users u ON r.user_id = u.id
JOIN bookings b ON r.booking_id = b.id
WHERE r.status IN ('pending', 'approved', 'processing')
ORDER BY r.created_at ASC;

-- =============================================================================
-- SAMPLE DATA FOR NEW TABLES
-- =============================================================================

-- Sample complaint
INSERT INTO complaints (
    user_id, booking_id, complaint_type, subject, description, priority, status
) VALUES (
    1, 1, 'service_quality', 'AC not cooling properly', 
    'The AC service was done but the AC is still not cooling properly', 
    'high', 'open'
);

-- =============================================================================
-- END OF ADDITIONS
-- =============================================================================

