# 📋 IMPLEMENTATION PLAN: Phase 1, Task 1.2
## **Ops Dashboard APIs - Metrics Endpoint**

**Date**: 2025-10-15  
**Status**: Planning Complete - Ready for Implementation  
**Previous Task**: Task 1.1 (Priority Queue) ✅ Complete

---

## 🎯 OBJECTIVE

Create a comprehensive metrics endpoint for the operations dashboard that provides real-time statistics and insights for operational decision-making.

---

## 📊 METRICS TO IMPLEMENT

### 1. **Bookings Metrics**
- Count by status (pending, confirmed, in_progress, completed, cancelled)
- Today's bookings count
- This week's bookings count
- This month's bookings count
- Bookings growth rate (vs previous period)

### 2. **Complaints Metrics**
- Count by priority (low, medium, high, critical)
- Count by status (open, in_progress, resolved, closed, escalated)
- Today's complaints count
- Unresolved complaints count
- Average resolution time

### 3. **SLA Metrics**
- Complaints at risk (within buffer time)
- Complaints breached (past due date)
- SLA compliance rate (%)
- Average response time
- Average resolution time

### 4. **Revenue Metrics**
- Total revenue (all time)
- Revenue by booking status
- Today's revenue
- This week's revenue
- This month's revenue
- Average order value (AOV)
- Revenue growth rate (vs previous period)

### 5. **Real-Time Stats**
- Active bookings (in_progress)
- Pending bookings (pending, confirmed)
- Active complaints (open, in_progress)
- Critical complaints count
- Staff workload (assigned items per staff)

---

## 🏗️ ARCHITECTURE

### **Endpoint Design**
```
GET /api/v1/ops/dashboard/metrics
```

**Query Parameters**:
- `period` (optional): "today", "week", "month", "all" (default: "all")
- `include` (optional): Comma-separated list of metric groups
  - "bookings", "complaints", "sla", "revenue", "realtime"
  - Default: all groups

**Response Structure**:
```json
{
  "period": "all",
  "generated_at": "2025-10-15T10:30:00Z",
  "bookings": {
    "by_status": {...},
    "today": 15,
    "week": 87,
    "month": 342,
    "growth_rate": 12.5
  },
  "complaints": {
    "by_priority": {...},
    "by_status": {...},
    "today": 8,
    "unresolved": 23,
    "avg_resolution_hours": 18.5
  },
  "sla": {
    "at_risk": 5,
    "breached": 2,
    "compliance_rate": 94.2,
    "avg_response_hours": 2.3,
    "avg_resolution_hours": 18.5
  },
  "revenue": {
    "total": 1250000.00,
    "by_status": {...},
    "today": 45000.00,
    "week": 285000.00,
    "month": 1250000.00,
    "average_order_value": 3654.76,
    "growth_rate": 8.3
  },
  "realtime": {
    "active_bookings": 12,
    "pending_bookings": 8,
    "active_complaints": 15,
    "critical_complaints": 2,
    "staff_workload": {...}
  }
}
```

---

## 📁 FILES TO CREATE

### 1. **Repository Layer**
**File**: `backend/src/repositories/metrics_repository.py`
- `get_bookings_by_status(period)` - Count bookings by status
- `get_complaints_by_priority(period)` - Count complaints by priority
- `get_complaints_by_status(period)` - Count complaints by status
- `get_sla_metrics(period)` - SLA compliance metrics
- `get_revenue_metrics(period)` - Revenue statistics
- `get_realtime_stats()` - Real-time dashboard stats
- `get_staff_workload()` - Staff assignment counts

### 2. **Service Layer**
**File**: `backend/src/services/metrics_service.py`
- `get_dashboard_metrics(period, include_groups)` - Main method
- `_get_bookings_metrics(period)` - Bookings metrics
- `_get_complaints_metrics(period)` - Complaints metrics
- `_get_sla_metrics(period)` - SLA metrics
- `_get_revenue_metrics(period)` - Revenue metrics
- `_get_realtime_metrics()` - Real-time metrics
- `_calculate_growth_rate(current, previous)` - Growth calculation

### 3. **Schemas**
**File**: `backend/src/schemas/metrics.py`
- `BookingsMetrics` - Bookings statistics
- `ComplaintsMetrics` - Complaints statistics
- `SLAMetrics` - SLA compliance metrics
- `RevenueMetrics` - Revenue statistics
- `RealtimeMetrics` - Real-time stats
- `DashboardMetricsResponse` - Complete response

### 4. **Routes**
**File**: `backend/src/api/v1/routes/ops.py` (modify existing)
- Add `GET /api/v1/ops/dashboard/metrics` endpoint

### 5. **Tests**
**File**: `backend/tests/unit/services/test_metrics_service.py`
- Test bookings metrics calculation
- Test complaints metrics calculation
- Test SLA metrics calculation
- Test revenue metrics calculation
- Test realtime metrics calculation
- Test growth rate calculation
- Test period filtering
- Test include groups filtering

---

## 🔒 SECURITY & PERMISSIONS

### **Permission Required**
- `ops.read` - Basic metrics access
- `ops.admin` - Full metrics including sensitive revenue data

### **Permission-Based Filtering**
- Users with `ops.read`: Can see all metrics except detailed revenue
- Users with `ops.admin`: Can see all metrics including revenue details

### **Audit Logging**
- Log all metrics access with:
  - Staff ID
  - Action: "view_metrics"
  - Resource type: "dashboard_metrics"
  - Period requested
  - Include groups requested
  - Timestamp

---

## ⚡ PERFORMANCE OPTIMIZATIONS

### **Caching Strategy**
- Cache metrics for 5 minutes (configurable via OpsConfig)
- Cache key: `metrics:{period}:{include_groups}`
- Invalidate on new booking/complaint creation

### **Query Optimization**
- Use COUNT() aggregations instead of fetching all records
- Use indexes on status, priority, created_at columns
- Parallel execution of independent metric queries
- Limit date range queries with proper indexes

### **Database Indexes** (already exist)
- `idx_status` on bookings.status
- `idx_status` on complaints.status
- `idx_priority` on complaints.priority
- `idx_created` on bookings.created_at
- `idx_created` on complaints.created_at
- `idx_sla` on complaints (response_due_at, resolution_due_at)

---

## 📝 IMPLEMENTATION STEPS

### **Step 1: Create Repository Layer**
1. Create `metrics_repository.py`
2. Implement all query methods
3. Add proper error handling
4. Add query optimization (use COUNT, indexes)

### **Step 2: Create Service Layer**
5. Create `metrics_service.py`
6. Implement main `get_dashboard_metrics` method
7. Implement individual metric methods
8. Add growth rate calculation
9. Add period filtering logic
10. Add include groups filtering
11. Add caching logic

### **Step 3: Create Schemas**
12. Create `metrics.py` schemas
13. Define all response models
14. Add field descriptions
15. Add examples

### **Step 4: Create API Endpoint**
16. Add metrics endpoint to `ops.py`
17. Add query parameter validation
18. Add permission checking
19. Add audit logging
20. Add error handling

### **Step 5: Create Tests**
21. Create `test_metrics_service.py`
22. Write unit tests for all methods
23. Test period filtering
24. Test include groups filtering
25. Test growth rate calculation
26. Test error scenarios

### **Step 6: Documentation**
27. Add API documentation
28. Add code comments
29. Create implementation summary

### **Step 7: Testing & Commit**
30. Run all unit tests
31. Manual API testing
32. Commit to feature branch
33. Merge to master

---

## 🎯 SUCCESS CRITERIA

- ✅ All metrics endpoints return correct data
- ✅ Period filtering works correctly
- ✅ Include groups filtering works correctly
- ✅ Growth rate calculation is accurate
- ✅ SLA metrics are calculated correctly
- ✅ Revenue metrics are accurate
- ✅ Permission-based access control works
- ✅ Audit logging captures all access
- ✅ Caching improves performance
- ✅ All unit tests pass (target: 10+ tests)
- ✅ Code is well-documented
- ✅ API documentation is complete

---

## 📊 ESTIMATED METRICS

- **Files to Create**: 3 (repository, service, schemas)
- **Files to Modify**: 2 (routes, __init__)
- **Lines of Code**: ~800-1000
- **Unit Tests**: 10-12
- **Time Estimate**: 2-3 hours

---

## 🔄 DEPENDENCIES

### **Existing Code**
- ✅ Booking model (status, payment_status, amounts)
- ✅ Complaint model (priority, status, SLA fields)
- ✅ OpsConfig (for cache TTL configuration)
- ✅ AuditService (for logging)
- ✅ Authentication middleware (for permission checking)

### **Database Tables**
- ✅ bookings (with status, amounts, created_at)
- ✅ complaints (with priority, status, SLA fields)
- ✅ staff (for workload calculation)
- ✅ ops_config (for configuration)
- ✅ ops_audit_log (for audit trail)

---

## 🚀 READY FOR IMPLEMENTATION

**Plan Status**: ✅ Complete  
**Next Step**: Create feature branch and start implementation

---

**Questions Resolved**:
1. ✅ What metrics to include? - Defined 5 metric groups
2. ✅ How to structure response? - Nested JSON with metric groups
3. ✅ How to handle permissions? - ops.read for basic, ops.admin for revenue
4. ✅ How to optimize performance? - Caching + query optimization
5. ✅ How to handle periods? - Query parameter with date filtering
6. ✅ How to make it flexible? - Include groups parameter

**Ready to proceed with implementation!** 🎉

