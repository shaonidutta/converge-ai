-- OPTIMIZED PINCODE DESIGN
-- Replace JSON array with proper relational tables

-- 1. Create pincodes master table
CREATE TABLE pincodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pincode VARCHAR(6) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    is_serviceable BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_pincode (pincode),
    INDEX idx_city (city),
    INDEX idx_state (state),
    INDEX idx_serviceable (is_serviceable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create rate_card_pincodes junction table (many-to-many)
CREATE TABLE rate_card_pincodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rate_card_id INT NOT NULL,
    pincode_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rate_card_id) REFERENCES rate_cards(id) ON DELETE CASCADE,
    FOREIGN KEY (pincode_id) REFERENCES pincodes(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_rate_card_pincode (rate_card_id, pincode_id),
    INDEX idx_rate_card (rate_card_id),
    INDEX idx_pincode (pincode_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Create provider_pincodes junction table (many-to-many)
CREATE TABLE provider_pincodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_id INT NOT NULL,
    pincode_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    FOREIGN KEY (pincode_id) REFERENCES pincodes(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_provider_pincode (provider_id, pincode_id),
    INDEX idx_provider (provider_id),
    INDEX idx_pincode (pincode_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Remove JSON columns from existing tables (migration)
-- ALTER TABLE rate_cards DROP COLUMN available_pincodes;
-- ALTER TABLE providers DROP COLUMN service_pincodes;

-- ============================================================================
-- BENEFITS OF THIS DESIGN
-- ============================================================================

-- 1. EFFICIENT QUERIES
-- Find all rate cards available in a pincode
SELECT rc.* 
FROM rate_cards rc
JOIN rate_card_pincodes rcp ON rc.id = rcp.rate_card_id
JOIN pincodes p ON rcp.pincode_id = p.id
WHERE p.pincode = '400001';

-- 2. INDEXED LOOKUPS (FAST)
-- Find all pincodes for a rate card
SELECT p.pincode, p.city, p.state
FROM pincodes p
JOIN rate_card_pincodes rcp ON p.id = rcp.pincode_id
WHERE rcp.rate_card_id = 123;

-- 3. EASY MANAGEMENT
-- Add pincode to rate card
INSERT INTO rate_card_pincodes (rate_card_id, pincode_id)
SELECT 123, id FROM pincodes WHERE pincode = '400001';

-- Remove pincode from rate card
DELETE FROM rate_card_pincodes 
WHERE rate_card_id = 123 AND pincode_id = (SELECT id FROM pincodes WHERE pincode = '400001');

-- 4. BULK OPERATIONS
-- Add multiple pincodes to a rate card
INSERT INTO rate_card_pincodes (rate_card_id, pincode_id)
SELECT 123, id FROM pincodes WHERE city = 'Mumbai';

-- 5. ANALYTICS
-- Count how many rate cards serve each pincode
SELECT p.pincode, p.city, COUNT(rcp.rate_card_id) as rate_card_count
FROM pincodes p
LEFT JOIN rate_card_pincodes rcp ON p.id = rcp.pincode_id
GROUP BY p.id, p.pincode, p.city
ORDER BY rate_card_count DESC;

-- 6. FIND PROVIDERS AND RATE CARDS FOR A PINCODE
SELECT 
    p.pincode,
    p.city,
    COUNT(DISTINCT pr.id) as provider_count,
    COUNT(DISTINCT rc.id) as rate_card_count
FROM pincodes p
LEFT JOIN provider_pincodes pp ON p.id = pp.pincode_id
LEFT JOIN providers pr ON pp.provider_id = pr.id
LEFT JOIN rate_card_pincodes rcp ON p.id = rcp.pincode_id
LEFT JOIN rate_cards rc ON rcp.rate_card_id = rc.id
WHERE p.pincode = '400001'
GROUP BY p.id, p.pincode, p.city;

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert Mumbai pincodes
INSERT INTO pincodes (pincode, city, state) VALUES
('400001', 'Mumbai', 'Maharashtra'),
('400002', 'Mumbai', 'Maharashtra'),
('400003', 'Mumbai', 'Maharashtra'),
('400004', 'Mumbai', 'Maharashtra'),
('400005', 'Mumbai', 'Maharashtra');

-- Insert Delhi pincodes
INSERT INTO pincodes (pincode, city, state) VALUES
('110001', 'Delhi', 'Delhi'),
('110002', 'Delhi', 'Delhi'),
('110003', 'Delhi', 'Delhi'),
('110004', 'Delhi', 'Delhi'),
('110005', 'Delhi', 'Delhi');

-- Link rate card to pincodes
INSERT INTO rate_card_pincodes (rate_card_id, pincode_id)
SELECT 1, id FROM pincodes WHERE city = 'Mumbai' LIMIT 10;

-- ============================================================================
-- PERFORMANCE COMPARISON
-- ============================================================================

-- OLD WAY (JSON) - SLOW ❌
-- SELECT * FROM rate_cards 
-- WHERE JSON_CONTAINS(available_pincodes, '"400001"');
-- Problem: Full table scan, no index usage

-- NEW WAY (JUNCTION TABLE) - FAST ✅
-- SELECT rc.* FROM rate_cards rc
-- JOIN rate_card_pincodes rcp ON rc.id = rcp.rate_card_id
-- JOIN pincodes p ON rcp.pincode_id = p.id
-- WHERE p.pincode = '400001';
-- Benefit: Uses indexes, efficient JOIN

-- ============================================================================
-- MIGRATION STRATEGY
-- ============================================================================

-- Step 1: Create new tables (pincodes, rate_card_pincodes, provider_pincodes)
-- Step 2: Migrate existing JSON data to new tables
-- Step 3: Update application code to use new tables
-- Step 4: Drop JSON columns from rate_cards and providers
-- Step 5: Test thoroughly


