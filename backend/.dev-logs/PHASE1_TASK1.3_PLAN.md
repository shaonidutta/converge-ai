# 📋 IMPLEMENTATION PLAN: Phase 1, Task 1.3
## **Ops Alert System & Notifications**

**Date**: 2025-10-15  
**Status**: Planning Phase  
**Previous Tasks**: 
- Task 1.1 (Priority Queue API) ✅ Complete
- Task 1.2 (Metrics Dashboard API) ✅ Complete

---

## 🎯 OBJECTIVE

Create a comprehensive alert system for operational staff to receive real-time notifications about critical events, SLA breaches, and high-priority items requiring immediate attention.

---

## 📊 ALERT TYPES TO IMPLEMENT

### 1. **SLA Breach Alerts**
- **At-Risk Alerts**: Complaints approaching SLA deadline (within buffer time)
- **Breach Alerts**: Complaints that have exceeded SLA deadline
- **Severity Levels**: Warning (at-risk), Critical (breached)

### 2. **Priority Alerts**
- **Critical Complaints**: New critical priority complaints
- **High Priority Items**: High priority items in queue
- **Escalated Items**: Complaints that have been escalated

### 3. **System Alerts**
- **High Workload**: Staff member exceeds workload threshold
- **Unassigned Items**: Critical items unassigned for > X minutes
- **Payment Failures**: Failed payment transactions

### 4. **Custom Alerts**
- **Configurable Rules**: Admin-defined alert rules
- **Threshold-Based**: Trigger when metrics exceed thresholds
- **Time-Based**: Scheduled alerts (daily summaries, etc.)

---

## 🏗️ ARCHITECTURE

### **Database Schema**

#### **alerts Table**
```sql
CREATE TABLE alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(50) NOT NULL,  -- 'sla_breach', 'critical_complaint', etc.
    severity VARCHAR(20) NOT NULL,     -- 'info', 'warning', 'critical'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    resource_type VARCHAR(50),         -- 'complaint', 'booking', etc.
    resource_id BIGINT,
    assigned_to_staff_id BIGINT,       -- NULL for broadcast alerts
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL,
    dismissed_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    
    INDEX idx_staff_unread (assigned_to_staff_id, is_read, created_at),
    INDEX idx_type_severity (alert_type, severity, created_at),
    INDEX idx_resource (resource_type, resource_id),
    FOREIGN KEY (assigned_to_staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
```

#### **alert_rules Table**
```sql
CREATE TABLE alert_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    rule_type VARCHAR(50) NOT NULL,    -- 'sla', 'threshold', 'event'
    is_enabled BOOLEAN DEFAULT TRUE,
    conditions JSON NOT NULL,           -- Rule conditions
    alert_config JSON NOT NULL,         -- Alert configuration
    created_by_staff_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_enabled (is_enabled),
    FOREIGN KEY (created_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL
);
```

#### **alert_subscriptions Table**
```sql
CREATE TABLE alert_subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    staff_id BIGINT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    delivery_channels JSON,             -- ['in_app', 'email', 'sms']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_subscription (staff_id, alert_type),
    INDEX idx_staff_enabled (staff_id, is_enabled),
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
```

---

## 📁 FILES TO CREATE

### 1. **Models**
- `backend/src/core/models/alert.py` - Alert, AlertRule, AlertSubscription models

### 2. **Repository Layer**
- `backend/src/repositories/alert_repository.py`
  - `create_alert()` - Create new alert
  - `get_alerts_for_staff()` - Get staff's alerts (unread, all)
  - `get_alert_by_id()` - Get single alert
  - `mark_as_read()` - Mark alert as read
  - `mark_as_dismissed()` - Dismiss alert
  - `get_unread_count()` - Count unread alerts
  - `delete_expired_alerts()` - Cleanup expired alerts
  - `get_alert_rules()` - Get active alert rules
  - `create_alert_rule()` - Create new rule
  - `update_alert_rule()` - Update rule
  - `delete_alert_rule()` - Delete rule

### 3. **Service Layer**
- `backend/src/services/alert_service.py`
  - `create_alert()` - Create and distribute alert
  - `get_staff_alerts()` - Get alerts for staff
  - `mark_alert_read()` - Mark as read
  - `dismiss_alert()` - Dismiss alert
  - `get_unread_count()` - Get unread count
  - `check_sla_alerts()` - Check and create SLA alerts
  - `check_priority_alerts()` - Check priority items
  - `check_workload_alerts()` - Check staff workload
  - `evaluate_alert_rules()` - Evaluate custom rules
  - `broadcast_alert()` - Send to all staff
  - `cleanup_old_alerts()` - Remove expired alerts

### 4. **Background Tasks**
- `backend/src/tasks/alert_tasks.py`
  - `check_sla_breaches_task()` - Periodic SLA check (every 5 min)
  - `check_critical_items_task()` - Check critical items (every 10 min)
  - `cleanup_alerts_task()` - Cleanup old alerts (daily)
  - `send_daily_summary_task()` - Daily summary (scheduled)

### 5. **Schemas**
- `backend/src/schemas/alert.py`
  - `AlertCreate` - Create alert request
  - `AlertResponse` - Alert response
  - `AlertListResponse` - Paginated alerts
  - `AlertRuleCreate` - Create rule request
  - `AlertRuleResponse` - Rule response
  - `AlertSubscriptionUpdate` - Update subscription

### 6. **Routes**
- `backend/src/api/v1/routes/alerts.py` (new file)
  - `GET /api/v1/alerts` - Get staff's alerts
  - `GET /api/v1/alerts/{id}` - Get single alert
  - `PUT /api/v1/alerts/{id}/read` - Mark as read
  - `PUT /api/v1/alerts/{id}/dismiss` - Dismiss alert
  - `GET /api/v1/alerts/unread/count` - Get unread count
  - `GET /api/v1/alerts/rules` - Get alert rules (admin)
  - `POST /api/v1/alerts/rules` - Create rule (admin)
  - `PUT /api/v1/alerts/rules/{id}` - Update rule (admin)
  - `DELETE /api/v1/alerts/rules/{id}` - Delete rule (admin)
  - `GET /api/v1/alerts/subscriptions` - Get subscriptions
  - `PUT /api/v1/alerts/subscriptions` - Update subscriptions

### 7. **Tests**
- `backend/tests/unit/services/test_alert_service.py`
- `backend/tests/unit/tasks/test_alert_tasks.py`

### 8. **Migration**
- `backend/migrations/add_alert_tables.sql`

---

## 🔒 SECURITY & PERMISSIONS

### **Permissions Required**
- `alerts.read` - View own alerts
- `alerts.manage` - Manage alert rules (admin)
- `alerts.broadcast` - Send broadcast alerts (admin)

### **Access Control**
- Staff can only see their own alerts
- Admins can see all alerts
- Alert rules require admin permission
- Broadcast alerts require special permission

---

## ⚡ ALERT GENERATION LOGIC

### **SLA Breach Detection**
```python
# Check every 5 minutes
1. Query complaints with response_due_at or resolution_due_at
2. Calculate time until deadline
3. If within buffer time (1 hour): Create "at_risk" alert
4. If past deadline: Create "breached" alert
5. Assign to complaint owner or broadcast
```

### **Critical Complaint Detection**
```python
# Check on complaint creation and priority change
1. If priority == CRITICAL: Create immediate alert
2. Assign to available staff or broadcast
3. Set severity = CRITICAL
```

### **Workload Threshold**
```python
# Check every 10 minutes
1. Get staff workload from metrics
2. If assigned_items > threshold (configurable): Create alert
3. Notify staff and their manager
```

---

## 📊 ALERT DELIVERY

### **In-App Notifications** (Phase 1)
- Store in database
- Retrieve via API
- Display in dashboard
- Real-time count updates

### **Future Enhancements** (Phase 2)
- Email notifications
- SMS notifications
- WebSocket push notifications
- Mobile push notifications

---

## 🎯 SUCCESS CRITERIA

- ✅ Alert database tables created
- ✅ Alert models and schemas defined
- ✅ Alert repository with CRUD operations
- ✅ Alert service with business logic
- ✅ Background tasks for periodic checks
- ✅ API endpoints for alert management
- ✅ SLA breach alerts working
- ✅ Critical complaint alerts working
- ✅ Alert rules system functional
- ✅ Permission-based access control
- ✅ Unit tests passing (target: 12+ tests)
- ✅ Integration with existing metrics
- ✅ Cleanup mechanism for old alerts

---

## 📈 ESTIMATED METRICS

- **Files to Create**: 8 (models, repository, service, tasks, schemas, routes, tests, migration)
- **Files to Modify**: 3 (__init__ files, main router)
- **Lines of Code**: ~1200-1500
- **Unit Tests**: 12-15
- **Database Tables**: 3 (alerts, alert_rules, alert_subscriptions)
- **API Endpoints**: 10
- **Background Tasks**: 4
- **Time Estimate**: 3-4 hours

---

## 🔄 IMPLEMENTATION STEPS

### **Phase 1: Database & Models** (30 min)
1. Create migration SQL
2. Create Alert, AlertRule, AlertSubscription models
3. Run migration

### **Phase 2: Repository Layer** (45 min)
4. Create AlertRepository
5. Implement CRUD methods
6. Add query methods

### **Phase 3: Service Layer** (60 min)
7. Create AlertService
8. Implement alert creation logic
9. Implement SLA check logic
10. Implement priority check logic
11. Implement rule evaluation

### **Phase 4: Background Tasks** (30 min)
12. Create alert_tasks.py
13. Implement periodic check tasks
14. Configure Celery tasks

### **Phase 5: API Endpoints** (45 min)
15. Create alerts.py routes
16. Implement all endpoints
17. Add permission checks
18. Add error handling

### **Phase 6: Schemas** (20 min)
19. Create alert schemas
20. Add validation
21. Add examples

### **Phase 7: Testing** (60 min)
22. Write unit tests for service
23. Write unit tests for tasks
24. Run all tests

### **Phase 8: Integration** (30 min)
25. Integrate with metrics service
26. Test end-to-end flow
27. Documentation

---

## 🚀 READY FOR IMPLEMENTATION

**Plan Status**: ✅ Complete  
**Next Step**: Get approval and start implementation

---

**Questions to Clarify**:
1. ✅ Alert types defined
2. ✅ Database schema designed
3. ✅ Delivery mechanism (in-app for Phase 1)
4. ✅ Background task frequency
5. ✅ Alert retention policy (30 days default)
6. ✅ Permission structure

**Ready to proceed with implementation!** 🎉

