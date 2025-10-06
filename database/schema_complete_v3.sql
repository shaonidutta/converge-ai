-- ConvergeAI - Complete Production-Ready MySQL Schema
-- Version: 3.0 (Production Ready)
-- Database: MySQL 8.0+
-- Total Tables: 12 (10 original + 2 for complaints)
-- Philosophy: Minimal but Complete - Ready for Production Launch

-- =============================================================================
-- DROP TABLES (in reverse order of dependencies)
-- =============================================================================

DROP TABLE IF EXISTS complaint_updates;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS priority_queue;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS booking_items;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS rate_cards;
DROP TABLE IF EXISTS subcategories;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- 1. Users
CREATE TABLE users (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    mobile VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Wallet
    wallet_balance DECIMAL(10,2) DEFAULT 0.00,
    
    -- Referral
    referral_code VARCHAR(20) UNIQUE,
    referred_by BIGINT UNSIGNED,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_mobile (mobile),
    INDEX idx_referral (referral_code),
    FOREIGN KEY (referred_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Categories
CREATE TABLE categories (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    image VARCHAR(500),
    
    -- Display
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_active (is_active, display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Subcategories
CREATE TABLE subcategories (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    category_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(500),
    
    -- Display
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id, is_active),
    UNIQUE KEY unique_slug (category_id, slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Rate Cards
CREATE TABLE rate_cards (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    category_id INT UNSIGNED NOT NULL,
    subcategory_id INT UNSIGNED NOT NULL,
    
    -- Pricing
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    strike_price DECIMAL(10,2),
    
    -- Availability (JSON array of pincodes)
    available_pincodes JSON,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE,
    INDEX idx_category_sub (category_id, subcategory_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Addresses
CREATE TABLE addresses (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Address
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    
    -- Contact
    contact_name VARCHAR(100),
    contact_mobile VARCHAR(15),
    
    -- Flags
    is_default BOOLEAN DEFAULT FALSE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_pincode (pincode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Providers
CREATE TABLE providers (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    
    -- Basic Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    mobile VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(255),
    
    -- Service Coverage (JSON array of pincodes)
    service_pincodes JSON,
    
    -- Rating
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    total_bookings INT DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_mobile (mobile),
    INDEX idx_active (is_active, is_verified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Bookings
CREATE TABLE bookings (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    
    -- Order
    order_id VARCHAR(50) UNIQUE NOT NULL,
    invoice_number VARCHAR(100),
    
    -- Payment
    payment_gateway_order_id VARCHAR(100),
    transaction_id VARCHAR(255),
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    payment_method ENUM('card', 'upi', 'wallet', 'cash') DEFAULT 'card',
    
    -- Amounts
    subtotal DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0.00,
    
    -- GST Details
    sgst DECIMAL(5,2) DEFAULT 0.00,
    cgst DECIMAL(5,2) DEFAULT 0.00,
    igst DECIMAL(5,2) DEFAULT 0.00,
    sgst_amount DECIMAL(10,2) DEFAULT 0.00,
    cgst_amount DECIMAL(10,2) DEFAULT 0.00,
    igst_amount DECIMAL(10,2) DEFAULT 0.00,
    total_gst DECIMAL(10,2) DEFAULT 0.00,
    
    -- Additional Charges
    convenience_charge DECIMAL(10,2) DEFAULT 0.00,
    
    -- Total
    total DECIMAL(10,2) NOT NULL,
    
    -- Partial Payment
    is_partial BOOLEAN DEFAULT FALSE,
    partial_amount DECIMAL(10,2) DEFAULT 0.00,
    remaining_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- Settlement
    is_settlement ENUM('pending', 'complete', 'failed', 'inprogress') DEFAULT 'pending',
    
    -- Status
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_payment (payment_status),
    INDEX idx_settlement (is_settlement),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Booking Items
CREATE TABLE booking_items (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    booking_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    rate_card_id INT UNSIGNED NOT NULL,
    provider_id BIGINT UNSIGNED,
    address_id BIGINT UNSIGNED NOT NULL,
    
    -- Service Details
    service_name VARCHAR(255) NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    
    -- Amounts
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    
    -- Scheduling
    scheduled_date DATE NOT NULL,
    scheduled_time_from TIME NOT NULL,
    scheduled_time_to TIME NOT NULL,
    
    -- Execution
    actual_start_time DATETIME,
    actual_end_time DATETIME,
    
    -- Cancellation
    cancel_by ENUM('', 'provider', 'customer') DEFAULT '',
    cancel_reason TEXT,
    
    -- Payment
    payment_status ENUM('unpaid', 'paid', 'refund', 'failed') DEFAULT 'unpaid',
    
    -- Status
    status ENUM('pending', 'accepted', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (rate_card_id) REFERENCES rate_cards(id) ON DELETE RESTRICT,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE SET NULL,
    FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE RESTRICT,
    INDEX idx_booking (booking_id),
    INDEX idx_user (user_id),
    INDEX idx_provider (provider_id, status),
    INDEX idx_payment (payment_status),
    INDEX idx_scheduled (scheduled_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- AI/AGENT TABLES
-- =============================================================================

-- 9. Conversations
CREATE TABLE conversations (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED,
    session_id VARCHAR(100) NOT NULL,
    
    -- Message
    role ENUM('user', 'assistant') NOT NULL,
    message TEXT NOT NULL,
    
    -- NLP
    intent VARCHAR(50),
    intent_confidence DECIMAL(4,3),
    
    -- Agent Execution (JSON for flexibility)
    agent_calls JSON COMMENT 'Array of agent execution details',
    
    -- Provenance (JSON for source tracking)
    provenance JSON COMMENT 'Sources used: SQL tables, vector docs, etc',
    
    -- Quality Metrics
    grounding_score DECIMAL(4,3),
    faithfulness_score DECIMAL(4,3),
    relevancy_score DECIMAL(4,3),
    response_time_ms INT,
    
    -- Review Flag
    flagged_for_review BOOLEAN DEFAULT FALSE,
    review_reason VARCHAR(255),
    
    -- Metadata
    channel ENUM('web', 'mobile', 'whatsapp') DEFAULT 'web',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_session (session_id),
    INDEX idx_user (user_id),
    INDEX idx_intent (intent),
    INDEX idx_flagged (flagged_for_review),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Priority Queue (Operations)
CREATE TABLE priority_queue (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    
    -- Intent & Scoring
    intent_type ENUM('complaint', 'refund', 'cancellation', 'booking') NOT NULL,
    confidence_score DECIMAL(4,3) NOT NULL,
    priority_score INT NOT NULL,
    sentiment_score DECIMAL(4,3),
    
    -- Context
    message_snippet TEXT,
    
    -- Review Status
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by BIGINT UNSIGNED,
    reviewed_at DATETIME,
    action_taken TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_priority (is_reviewed, priority_score DESC, created_at DESC),
    INDEX idx_reviewed_by (reviewed_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- COMPLAINT MANAGEMENT TABLES (CRITICAL ADDITION)
-- =============================================================================

-- 11. Complaints
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
    INDEX idx_created (created_at),
    INDEX idx_sla (response_due_at, resolution_due_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Complaint Updates
CREATE TABLE complaint_updates (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    complaint_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,

    -- Update Details
    comment TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE COMMENT 'Internal notes not visible to customer',

    -- Attachments (optional)
    attachments JSON COMMENT 'Array of attachment URLs',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_complaint (complaint_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- SAMPLE DATA (for testing)
-- =============================================================================

-- Insert sample category
INSERT INTO categories (name, slug, description, image, display_order, is_active)
VALUES ('Home Cleaning', 'home-cleaning', 'Professional home cleaning services', 'https://example.com/cleaning.jpg', 1, TRUE);

-- Insert sample subcategory
INSERT INTO subcategories (category_id, name, slug, description, image, display_order, is_active)
VALUES (1, 'AC Service', 'ac-service', 'Split and Window AC servicing', 'https://example.com/ac.jpg', 1, TRUE);

-- Insert sample rate card
INSERT INTO rate_cards (category_id, subcategory_id, name, price, strike_price, available_pincodes, is_active)
VALUES (1, 1, 'Basic AC Service', 699.00, 999.00, JSON_ARRAY('400001', '400002', '400003'), TRUE);

-- Insert sample user
INSERT INTO users (mobile, email, first_name, last_name, wallet_balance, is_active)
VALUES ('9876543210', 'test@example.com', 'Test', 'User', 100.00, TRUE);

-- Insert sample provider
INSERT INTO providers (first_name, last_name, mobile, email, service_pincodes, is_active, is_verified)
VALUES ('John', 'Provider', '9876543211', 'provider@example.com', JSON_ARRAY('400001', '400002'), TRUE, TRUE);

-- =============================================================================
-- VIEWS (for common queries)
-- =============================================================================

-- Active rate cards with category and subcategory names
CREATE OR REPLACE VIEW v_active_rate_cards AS
SELECT
    rc.id,
    rc.name AS service_name,
    rc.price,
    rc.strike_price,
    CASE
        WHEN rc.strike_price IS NOT NULL AND rc.strike_price > rc.price
        THEN ROUND(((rc.strike_price - rc.price) / rc.strike_price) * 100, 0)
        ELSE 0
    END AS discount_percentage,
    c.name AS category_name,
    sc.name AS subcategory_name,
    rc.available_pincodes
FROM rate_cards rc
JOIN categories c ON rc.category_id = c.id
JOIN subcategories sc ON rc.subcategory_id = sc.id
WHERE rc.is_active = TRUE
  AND c.is_active = TRUE
  AND sc.is_active = TRUE;

-- Booking summary with user details
CREATE OR REPLACE VIEW v_booking_summary AS
SELECT
    b.id,
    b.order_id,
    b.invoice_number,
    u.mobile AS user_mobile,
    u.first_name AS user_name,
    b.subtotal,
    b.discount,
    b.total_gst,
    b.convenience_charge,
    b.total,
    b.is_partial,
    b.partial_amount,
    b.remaining_amount,
    b.status,
    b.payment_status,
    b.is_settlement,
    b.created_at
FROM bookings b
JOIN users u ON b.user_id = u.id;

-- Priority queue with user details
CREATE OR REPLACE VIEW v_priority_queue AS
SELECT
    pq.id,
    pq.intent_type,
    pq.priority_score,
    pq.sentiment_score,
    u.mobile AS user_mobile,
    u.first_name AS user_name,
    pq.message_snippet,
    pq.is_reviewed,
    pq.created_at
FROM priority_queue pq
JOIN users u ON pq.user_id = u.id
WHERE pq.is_reviewed = FALSE
ORDER BY pq.priority_score DESC, pq.created_at DESC;

-- Open complaints with user and booking details
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
    TIMESTAMPDIFF(HOUR, c.created_at, NOW()) AS hours_open,
    CASE
        WHEN c.response_due_at < NOW() AND c.status = 'open' THEN TRUE
        ELSE FALSE
    END AS response_overdue,
    CASE
        WHEN c.resolution_due_at < NOW() AND c.status IN ('open', 'in_progress') THEN TRUE
        ELSE FALSE
    END AS resolution_overdue
FROM complaints c
JOIN users u ON c.user_id = u.id
LEFT JOIN bookings b ON c.booking_id = b.id
LEFT JOIN users assigned ON c.assigned_to = assigned.id
WHERE c.status IN ('open', 'in_progress', 'escalated')
ORDER BY c.priority DESC, c.created_at ASC;

-- Complaint details with update count
CREATE OR REPLACE VIEW v_complaint_details AS
SELECT
    c.*,
    u.mobile AS user_mobile,
    u.first_name AS user_name,
    u.email AS user_email,
    b.order_id,
    assigned.first_name AS assigned_to_name,
    resolved.first_name AS resolved_by_name,
    COUNT(cu.id) AS update_count,
    MAX(cu.created_at) AS last_update_at
FROM complaints c
JOIN users u ON c.user_id = u.id
LEFT JOIN bookings b ON c.booking_id = b.id
LEFT JOIN users assigned ON c.assigned_to = assigned.id
LEFT JOIN users resolved ON c.resolved_by = resolved.id
LEFT JOIN complaint_updates cu ON c.id = cu.complaint_id
GROUP BY c.id;

-- =============================================================================
-- TRIGGERS (for automatic SLA calculation)
-- =============================================================================

DELIMITER //

-- Trigger to set SLA deadlines when complaint is created
CREATE TRIGGER set_complaint_sla
BEFORE INSERT ON complaints
FOR EACH ROW
BEGIN
    -- Set response due time based on priority
    SET NEW.response_due_at = CASE NEW.priority
        WHEN 'critical' THEN DATE_ADD(NOW(), INTERVAL 1 HOUR)
        WHEN 'high' THEN DATE_ADD(NOW(), INTERVAL 4 HOUR)
        WHEN 'medium' THEN DATE_ADD(NOW(), INTERVAL 24 HOUR)
        WHEN 'low' THEN DATE_ADD(NOW(), INTERVAL 48 HOUR)
    END;

    -- Set resolution due time based on priority
    SET NEW.resolution_due_at = CASE NEW.priority
        WHEN 'critical' THEN DATE_ADD(NOW(), INTERVAL 4 HOUR)
        WHEN 'high' THEN DATE_ADD(NOW(), INTERVAL 24 HOUR)
        WHEN 'medium' THEN DATE_ADD(NOW(), INTERVAL 72 HOUR)
        WHEN 'low' THEN DATE_ADD(NOW(), INTERVAL 168 HOUR)
    END;
END//

-- Trigger to set resolved_at when status changes to resolved
CREATE TRIGGER set_complaint_resolved
BEFORE UPDATE ON complaints
FOR EACH ROW
BEGIN
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        SET NEW.resolved_at = NOW();
    END IF;
END//

DELIMITER ;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
