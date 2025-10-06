# ConvergeAI - Database Schema

**Final MySQL Schema - Production Ready**

---

## 📊 Overview

- **Database:** MySQL 8.0+
- **Total Tables:** 10
- **Philosophy:** Simple, Clean, YAGNI (You Aren't Gonna Need It)
- **Status:** Production Ready

---

## 🎯 Schema Summary

### **Core Tables (7)**
1. **users** - User accounts, wallet, referrals
2. **categories** - Service categories
3. **subcategories** - Service subcategories
4. **rate_cards** - Pricing with pincode availability
5. **addresses** - User delivery addresses
6. **providers** - Service providers
7. **bookings** - Orders and payments
8. **booking_items** - Order line items with scheduling

### **AI/Agent Tables (3)**
9. **conversations** - Chat history with NLP results
10. **priority_queue** - Operations priority system

---

## 📈 Key Improvements

### From Original (21 tables) → Final (10 tables)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Tables** | 21 | 10 | **52% reduction** |
| **Columns** | ~180 | ~80 | **56% reduction** |
| **Complexity** | High | Low | **Much simpler** |
| **Joins** | Many | Few | **Faster queries** |

---

## ✅ Best Practices Followed

### 1. MySQL Specific
- ✅ InnoDB engine (ACID, foreign keys)
- ✅ UTF8MB4 charset (emoji support)
- ✅ DATETIME for timestamps (not BIGINT)
- ✅ DECIMAL for money (not FLOAT)
- ✅ UNSIGNED for IDs
- ✅ Proper indexes on foreign keys

### 2. Naming Conventions
- ✅ snake_case (lowercase with underscores)
- ✅ Plural table names (users, bookings)
- ✅ Clear, descriptive names
- ✅ No abbreviations

### 3. Data Integrity
- ✅ Foreign keys with ON DELETE actions
- ✅ NOT NULL where appropriate
- ✅ DEFAULT values
- ✅ UNIQUE constraints
- ✅ Proper ENUM types

### 4. Performance
- ✅ Indexes on foreign keys
- ✅ Composite indexes for common queries
- ✅ No over-indexing
- ✅ Efficient data types

### 5. YAGNI Principle
- ✅ Only columns needed NOW
- ✅ No speculative features
- ✅ Add complexity later when needed

---

## 🚀 Quick Start

### 1. Create Database
```bash
mysql -u root -p
```

```sql
CREATE DATABASE convergeai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE convergeai;
```

### 2. Run Schema
```bash
mysql -u root -p convergeai < schema.sql
```

### 3. Verify
```sql
SHOW TABLES;
-- Should show 10 tables

SELECT * FROM v_active_rate_cards;
-- Should show sample rate card
```

---

## 📝 Common Queries

### Get available services for a pincode
```sql
SELECT 
    c.name AS category,
    sc.name AS subcategory,
    rc.name AS service,
    rc.price
FROM rate_cards rc
JOIN categories c ON rc.category_id = c.id
JOIN subcategories sc ON rc.subcategory_id = sc.id
WHERE rc.is_active = TRUE
  AND JSON_CONTAINS(rc.available_pincodes, '"400001"')
ORDER BY c.display_order, sc.display_order;
```

### Get user's booking history
```sql
SELECT 
    b.order_id,
    b.total,
    b.status,
    b.created_at,
    GROUP_CONCAT(bi.service_name) AS services
FROM bookings b
JOIN booking_items bi ON b.id = bi.booking_id
WHERE b.user_id = 1
GROUP BY b.id
ORDER BY b.created_at DESC;
```

### Get priority queue for operations
```sql
SELECT * FROM v_priority_queue
LIMIT 50;
```

### Get provider's upcoming bookings
```sql
SELECT 
    bi.id,
    bi.service_name,
    bi.scheduled_date,
    bi.scheduled_time_from,
    u.first_name AS customer_name,
    u.mobile AS customer_mobile,
    a.address_line1,
    a.pincode
FROM booking_items bi
JOIN bookings b ON bi.booking_id = b.id
JOIN users u ON b.user_id = u.id
JOIN addresses a ON bi.address_id = a.id
WHERE bi.provider_id = 1
  AND bi.status IN ('pending', 'accepted')
  AND bi.scheduled_date >= CURDATE()
ORDER BY bi.scheduled_date, bi.scheduled_time_from;
```

---

## 🔧 Maintenance

### Backup
```bash
# Full backup
mysqldump -u root -p convergeai > backup_$(date +%Y%m%d).sql

# Schema only
mysqldump -u root -p --no-data convergeai > schema_backup.sql

# Data only
mysqldump -u root -p --no-create-info convergeai > data_backup.sql
```

### Restore
```bash
mysql -u root -p convergeai < backup_20250105.sql
```

### Optimize
```sql
-- Analyze tables
ANALYZE TABLE users, bookings, booking_items;

-- Optimize tables
OPTIMIZE TABLE users, bookings, booking_items;

-- Check table status
SHOW TABLE STATUS;
```

---

## 📊 Indexes

### Existing Indexes
```sql
-- Show all indexes
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'convergeai'
GROUP BY TABLE_NAME, INDEX_NAME;
```

### Add Custom Indexes (if needed)
```sql
-- Example: Index on booking date range queries
CREATE INDEX idx_booking_date_range 
ON booking_items (scheduled_date, status);

-- Example: Index on user search
CREATE INDEX idx_user_search 
ON users (first_name, last_name);
```

---

## 🔐 Security

### Create Application User
```sql
-- Create user
CREATE USER 'convergeai_app'@'localhost' IDENTIFIED BY 'strong_password_here';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON convergeai.* TO 'convergeai_app'@'localhost';

-- No DELETE permission (use soft deletes in application)
-- No DROP permission (only admin should have)

FLUSH PRIVILEGES;
```

### Create Read-Only User (for analytics)
```sql
CREATE USER 'convergeai_readonly'@'localhost' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON convergeai.* TO 'convergeai_readonly'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📈 Monitoring

### Check Table Sizes
```sql
SELECT 
    TABLE_NAME,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb,
    TABLE_ROWS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'convergeai'
ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;
```

### Check Slow Queries
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2; -- queries taking > 2 seconds

-- Check slow queries
SELECT * FROM mysql.slow_log
ORDER BY start_time DESC
LIMIT 10;
```

### Check Index Usage
```sql
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    CARDINALITY
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'convergeai'
  AND CARDINALITY IS NOT NULL
ORDER BY TABLE_NAME, CARDINALITY DESC;
```

---

## 🧪 Testing

### Sample Data
```sql
-- Insert test user
INSERT INTO users (mobile, first_name, wallet_balance) 
VALUES ('9999999999', 'Test User', 500.00);

-- Insert test booking
INSERT INTO bookings (user_id, order_id, subtotal, total, status)
VALUES (1, 'ORD-TEST-001', 699.00, 699.00, 'pending');

-- Insert test booking item
INSERT INTO booking_items (
    booking_id, rate_card_id, address_id, 
    service_name, price, 
    scheduled_date, scheduled_time_from, scheduled_time_to
)
VALUES (
    1, 1, 1, 
    'AC Service', 699.00, 
    CURDATE() + INTERVAL 1 DAY, '10:00:00', '12:00:00'
);
```

### Cleanup Test Data
```sql
DELETE FROM booking_items WHERE booking_id IN (SELECT id FROM bookings WHERE order_id LIKE 'ORD-TEST-%');
DELETE FROM bookings WHERE order_id LIKE 'ORD-TEST-%';
DELETE FROM users WHERE mobile = '9999999999';
```

---

## 🔄 Migration from Existing DB

See `migration.sql` for complete migration script from `eassy_new_backup` to new schema.

Key steps:
1. Backup existing database
2. Create new database with new schema
3. Run migration script to copy data
4. Validate data integrity
5. Update application connection strings
6. Test thoroughly
7. Switch to new database

---

## 📚 Documentation

- **Schema Details:** See `FINAL_MYSQL_SCHEMA.md`
- **ER Diagram:** See Mermaid diagram in documentation
- **API Integration:** See application documentation

---

## 🆘 Troubleshooting

### Foreign Key Errors
```sql
-- Check foreign key constraints
SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'convergeai'
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Temporarily disable foreign key checks (use carefully!)
SET FOREIGN_KEY_CHECKS = 0;
-- ... your operations ...
SET FOREIGN_KEY_CHECKS = 1;
```

### Character Set Issues
```sql
-- Check character sets
SHOW VARIABLES LIKE 'character_set%';

-- Convert table to UTF8MB4
ALTER TABLE table_name 
CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Performance Issues
```sql
-- Check running queries
SHOW PROCESSLIST;

-- Kill long-running query
KILL QUERY process_id;

-- Check table locks
SHOW OPEN TABLES WHERE In_use > 0;
```

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review `FINAL_MYSQL_SCHEMA.md`
3. Check application logs
4. Contact database admin

---

**Version:** 1.0  
**Last Updated:** 2025-10-05  
**Status:** Production Ready
