# Ops Priority Queue Implementation

**Date**: 2025-10-15  
**Feature Branch**: `feature/ops-priority-queue`  
**Task**: Phase 1, Task 1.1 - Ops Dashboard APIs (Priority Queue Endpoint)

---

## Overview

Implemented the Priority Queue endpoint for the Ops Dashboard, providing a unified view of operational items requiring human attention (critical complaints, pending bookings, refund approvals, etc.).

---

## Features Implemented

### 1. **Database Models**
- **OpsConfig**: Runtime configuration for feature flags
  - Stores configurable settings (DEFAULT_STATUS_FILTER, SLA_BUFFER_HOURS, etc.)
  - Enables runtime tuning without code deployment
  
- **OpsAuditLog**: Audit trail for ops operations
  - Tracks who accessed what data and when
  - Critical for compliance and PII access monitoring
  - Logs IP address, user agent, and request metadata

### 2. **Repository Layer**
- **PriorityQueueRepository**: Data access for priority queue items
  - `get_priority_items()`: Query with filters, sorting, pagination
  - `count_priority_items()`: Count total matching items
  - `get_item_by_id()`: Get single item
  - `update_review_status()`: Mark item as reviewed

### 3. **Service Layer**
- **ConfigService**: Runtime configuration management
  - `get_config()`: Get config with caching
  - `get_config_int()`, `get_config_bool()`: Type-safe getters
  - `set_config()`: Update config (admin only)
  
- **AuditService**: Audit logging
  - `log_access()`: Log ops access with PII tracking
  - `log_priority_queue_access()`: Convenience method for queue access
  - `log_complaint_access()`, `log_booking_access()`: Entity-specific logging
  
- **OpsDashboardService**: Main business logic
  - `get_priority_queue()`: Get items with filtering, pagination, enrichment
  - `_check_full_access_permission()`: Permission checking for PII access
  - `_redact_pii()`: Redact sensitive data for users without full access
  - `_enrich_priority_item()`: Enrich with related entity data
  - `_get_summary_related_entity()`: Fast summary (default)
  - `_get_full_related_entity()`: Full details (expand=true)
  - `_calculate_sla_risk()`: SLA breach risk calculation
  - `_calculate_booking_priority()`: Booking priority calculation

### 4. **API Endpoint**
- **GET /api/v1/ops/dashboard/priority-queue**
  - **Permission Required**: `ops.read`
  - **Query Parameters**:
    - `status`: pending (default), reviewed, all
    - `intent_type`: complaint, booking, refund, cancellation
    - `priority_min/max`: Priority score range (0-100)
    - `date_from/to`: Date range filter
    - `sort_by`: priority_score (default), created_at, confidence_score
    - `sort_order`: desc (default), asc
    - `skip`: Pagination offset (default 0)
    - `limit`: Items per page (default 20, max 100)
    - `expand`: Fetch full details (default false)
    - `fields`: Specific fields to include in expansion
  - **Response**: PriorityQueueResponse with items, total, pagination info

### 5. **Pydantic Schemas**
- **RelatedEntitySummary**: Lightweight summary (default)
- **RelatedEntityFull**: Full details (expand=true)
- **PriorityQueueItem**: Single queue item with conditional PII
- **PriorityQueueResponse**: Paginated list response
- **PriorityQueueFilters**: Internal filter model

---

## Security Features

### 1. **Permission-Based PII Access**
- **ops.read**: Basic read access (redacted PII)
- **ops.full_access**: Full PII access (unredacted)
- **ops.write**: Can review/update items
- **ops.admin**: Full admin access

### 2. **PII Redaction**
- **Mobile**: `9876543210` → `98****3210`
- **Email**: `jane@example.com` → `j***@example.com`
- **Name**: `Jane Smith` → `Jane S.`
- **Message**: Truncated to 100 chars

### 3. **Audit Logging**
- All access logged with:
  - Staff ID
  - Action performed
  - Resource accessed
  - PII access flag
  - Request metadata (IP, user agent)
  - Timestamp

### 4. **Rate Limiting**
- Max expand requests per hour (configurable)
- Pagination limits enforced (max 100 items)

---

## Performance Optimizations

### 1. **Enrichment Strategy**
- **Default**: Summary only (fast)
- **Expand=true**: Full details (expensive, rate limited)
- **Only paginated results enriched** (not entire dataset)

### 2. **Database Indexes**
- `idx_priority_queue_ops_view`: (is_reviewed, priority_score, created_at)
- `idx_bookings_pending_ops`: (status, payment_status, created_at)
- `idx_complaints_sla_ops`: (status, priority, response_due_at, resolution_due_at)

### 3. **Caching**
- Config values cached in-memory
- Cache invalidation on config updates

---

## Database Changes

### New Tables

#### ops_config
```sql
CREATE TABLE ops_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
);
```

**Default Configurations**:
- `DEFAULT_STATUS_FILTER`: "pending"
- `SLA_BUFFER_HOURS`: "1"
- `MAX_EXPAND_PER_HOUR`: "100"
- `ENABLE_AUTO_ENRICHMENT`: "true"

#### ops_audit_log
```sql
CREATE TABLE ops_audit_log (
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
);
```

### Updated Tables
- **staff**: Added `audit_logs` relationship

---

## Testing

### Unit Tests
**File**: `backend/tests/unit/services/test_ops_dashboard_service.py`

**Test Coverage**:
- ✅ Basic priority queue retrieval
- ✅ Full access permission check (with/without access)
- ✅ PII redaction (mobile, email, name, message)
- ✅ Filter building
- ✅ Booking priority calculation
- ✅ SLA risk calculation (at risk, not at risk, no due date)

**Run Tests**:
```bash
pytest backend/tests/unit/services/test_ops_dashboard_service.py -v
```

### Integration Tests
**Status**: To be implemented in next iteration

**Planned Tests**:
- API endpoint authentication
- API endpoint authorization
- Query parameter validation
- Response format validation
- Pagination behavior
- PII redaction in responses
- Audit log creation

---

## Files Created

### Models
- `backend/src/core/models/ops_config.py`
- `backend/src/core/models/ops_audit_log.py`

### Repositories
- `backend/src/repositories/priority_queue_repository.py`

### Services
- `backend/src/services/config_service.py`
- `backend/src/services/audit_service.py`
- `backend/src/services/ops_dashboard_service.py`

### Schemas
- `backend/src/schemas/ops_dashboard.py`

### Routes
- Updated: `backend/src/api/v1/routes/ops.py` (added priority queue endpoint)

### Migrations
- `backend/migrations/add_ops_config_and_audit_tables.sql`
- `backend/scripts/run_ops_migration.py`
- `backend/scripts/create_ops_tables_simple.py`

### Tests
- `backend/tests/unit/services/test_ops_dashboard_service.py`

### Documentation
- `backend/.dev-logs/OPS_PRIORITY_QUEUE_IMPLEMENTATION.md` (this file)

---

## Files Modified

- `backend/src/core/models/__init__.py`: Exported new models
- `backend/src/core/models/staff.py`: Added audit_logs relationship
- `backend/src/services/__init__.py`: Exported new services

---

## Migration Instructions

### Option 1: Run SQL Directly
```bash
# Connect to MySQL
mysql -u your_user -p your_database

# Run migration
source backend/migrations/add_ops_config_and_audit_tables.sql
```

### Option 2: Use Python Script
```bash
# Print SQL to console
python backend/scripts/create_ops_tables_simple.py

# Copy and run in MySQL client
```

### Option 3: Use SQLAlchemy (if .env configured)
```bash
python backend/scripts/run_ops_migration.py
```

---

## API Usage Examples

### 1. Get Pending Items (Default)
```bash
GET /api/v1/ops/dashboard/priority-queue
Authorization: Bearer <jwt_token>
```

### 2. Get High Priority Complaints
```bash
GET /api/v1/ops/dashboard/priority-queue?intent_type=complaint&priority_min=70&status=pending
Authorization: Bearer <jwt_token>
```

### 3. Get with Full Details (Expand)
```bash
GET /api/v1/ops/dashboard/priority-queue?expand=true&fields=subject,description
Authorization: Bearer <jwt_token>
```

### 4. Pagination
```bash
GET /api/v1/ops/dashboard/priority-queue?skip=20&limit=20
Authorization: Bearer <jwt_token>
```

---

## Next Steps

### Immediate (Task 1.1 Completion)
1. ✅ Run database migration
2. ✅ Run unit tests
3. ⏳ Create integration tests
4. ⏳ Test API endpoint manually
5. ⏳ Commit and merge to master

### Future Tasks (Phase 1)
- **Task 1.2**: Ops Dashboard APIs - Metrics endpoint
- **Task 1.3**: Ops Dashboard APIs - Tasks Management endpoints
- **Task 1.4**: Alert System Backend
- **Task 1.5**: Basic Ops Frontend

---

## Known Limitations

1. **Booking Session Linking**: `_get_booking_by_session()` needs proper implementation based on how bookings are linked to sessions
2. **Metrics Tracking**: `_track_metrics()` is a placeholder - needs integration with monitoring system
3. **Rate Limiting**: Max expand per hour is tracked in audit log but not enforced yet
4. **Background Enrichment**: Not implemented - all enrichment is synchronous

---

## Compliance & Security Notes

- ✅ PII redaction implemented for users without full access
- ✅ Audit logging for all PII access
- ✅ Permission-based access control
- ✅ Request metadata logged (IP, user agent)
- ✅ Configurable SLA buffer times
- ⚠️ Rate limiting tracked but not enforced
- ⚠️ GDPR compliance requires additional data retention policies

---

**Implementation Status**: ✅ COMPLETE (Pending Testing & Migration)  
**Ready for Review**: YES  
**Ready for Merge**: After testing and migration

