# Development Workflow Best Practices

## Date: 2025-10-14

---

## 🎯 **GOAL: Minimize Fixes, Maximize Quality**

This document outlines the **proven workflow** to develop features with minimal bugs and rework.

---

## 📋 **THE GOLDEN WORKFLOW (7 Steps)**

### **Step 1: Research & Understand** 🔍
**Time**: 20-30% of total development time

**Actions**:
1. **Read Latest Documentation** (Context7 MCP)
   - Always check official docs for libraries/frameworks
   - Never assume API signatures - verify them
   - Example: LangChain, SQLAlchemy, Pydantic versions change

2. **Search Existing Codebase**
   - Use `codebase-retrieval` to find similar implementations
   - Check how existing features are structured
   - Look for patterns already established

3. **Check Database Schema**
   - Verify table structures before writing queries
   - Check column names, types, relationships
   - Use `view` tool to inspect models

4. **Understand Dependencies**
   - What services/classes will you use?
   - What are their exact method signatures?
   - What do they return?

**Example**:
```python
# ❌ BAD: Assuming field names
booking.total  # Might not exist!

# ✅ GOOD: Verify first
# 1. Check model: view backend/src/core/models/booking.py
# 2. Confirm field: total_amount (not total)
# 3. Use correct field: booking.total_amount
```

**Why This Matters**: 80% of bugs come from wrong assumptions about APIs, field names, or data structures.

---

### **Step 2: Plan & Design** 📐
**Time**: 10-15% of total development time

**Actions**:
1. **Write Down the Plan**
   - What files will you create/modify?
   - What methods/functions will you add?
   - What are the inputs/outputs?
   - What are the dependencies?

2. **Design Data Flow**
   - Request → Service → Repository → Database
   - Response flow back
   - Error handling at each layer

3. **Identify Edge Cases**
   - What if user doesn't exist?
   - What if database is down?
   - What if required field is missing?

4. **Check for Existing Patterns**
   - How did we implement similar features?
   - Can we reuse existing code?
   - Should we follow the same structure?

**Example Plan**:
```markdown
## Feature: Reschedule Booking

### Files to Modify:
- backend/src/agents/booking/booking_agent.py

### New Method:
- `_reschedule_booking(entities, user)` → Dict[str, Any]

### Dependencies:
- BookingService.get_booking_by_id()
- BookingService.update_booking()
- Provider availability validation

### Data Flow:
1. Extract booking_id, new_date, new_time from entities
2. Fetch booking from database
3. Validate booking belongs to user
4. Validate new date/time
5. Check provider availability
6. Update booking
7. Return success response

### Edge Cases:
- Booking not found
- Booking already completed
- New date in the past
- Provider not available
- Database error
```

---

### **Step 3: Write Tests First (TDD)** ✅
**Time**: 15-20% of total development time

**Actions**:
1. **Write Test Cases Before Implementation**
   - Happy path test
   - Edge case tests
   - Error handling tests

2. **Use Descriptive Test Names**
   ```python
   # ✅ GOOD
   def test_reschedule_booking_success_with_valid_date()
   def test_reschedule_booking_fails_when_booking_not_found()
   def test_reschedule_booking_fails_when_date_in_past()
   
   # ❌ BAD
   def test_reschedule()
   def test_booking()
   ```

3. **Mock External Dependencies**
   - Mock database calls
   - Mock external APIs
   - Mock LLM calls

4. **Run Tests (They Should Fail)**
   - Red → Green → Refactor cycle
   - Failing tests confirm you're testing the right thing

**Why This Matters**: Tests written first catch bugs before they exist. Tests written after often miss edge cases.

---

### **Step 4: Implement in Small Chunks** 🧩
**Time**: 30-40% of total development time

**Actions**:
1. **Implement One Method at a Time**
   - Don't write 500 lines at once
   - Implement, test, commit
   - Repeat

2. **Follow Existing Patterns**
   - Copy structure from similar methods
   - Use same error handling approach
   - Follow same naming conventions

3. **Use Type Hints**
   ```python
   # ✅ GOOD
   async def _reschedule_booking(
       self, 
       entities: Dict[str, Any], 
       user: User
   ) -> Dict[str, Any]:
       pass
   
   # ❌ BAD
   async def _reschedule_booking(self, entities, user):
       pass
   ```

4. **Add Comments for Complex Logic**
   ```python
   # Calculate refund based on cancellation policy
   # Full refund: >24 hours before scheduled time
   # 50% refund: 12-24 hours before
   # No refund: <12 hours before
   refund_amount = self._calculate_refund(booking, current_time)
   ```

5. **Handle Errors Gracefully**
   ```python
   try:
       booking = await self.booking_service.get_booking_by_id(booking_id)
   except BookingNotFoundError:
       return {
           "response": "❌ Booking not found. Please check your booking ID.",
           "action_taken": "error",
           "error_type": "booking_not_found"
       }
   ```

**Why This Matters**: Small chunks are easier to debug, test, and review.

---

### **Step 5: Test Thoroughly** 🧪
**Time**: 15-20% of total development time

**Actions**:
1. **Run Unit Tests**
   ```bash
   pytest backend/tests/test_booking_agent.py -v
   ```

2. **Run Integration Tests**
   ```bash
   pytest backend/tests/integration/test_booking_agent_integration.py -v
   ```

3. **Test Manually (If Needed)**
   - Create test script
   - Test with real database
   - Verify all fields populated correctly

4. **Check Test Coverage**
   ```bash
   pytest --cov=backend/src/agents/booking --cov-report=html
   ```
   - Aim for >80% coverage

5. **Test Edge Cases**
   - Invalid inputs
   - Missing fields
   - Database errors
   - Concurrent requests

**Why This Matters**: Bugs found in testing are 10x cheaper to fix than bugs found in production.

---

### **Step 6: Review & Refactor** 🔄
**Time**: 5-10% of total development time

**Actions**:
1. **Self-Review Code**
   - Read your own code as if you're reviewing someone else's
   - Check for code smells
   - Look for duplication

2. **Refactor for Clarity**
   - Extract complex logic into helper methods
   - Rename variables for clarity
   - Remove dead code

3. **Check Against Best Practices**
   - DRY (Don't Repeat Yourself)
   - SOLID principles
   - Clean code principles

4. **Update Documentation**
   - Add docstrings
   - Update README if needed
   - Add comments for complex logic

**Example Refactoring**:
```python
# ❌ BEFORE: Complex nested logic
if booking:
    if booking.user_id == user.id:
        if booking.status == "PENDING":
            if new_date > current_date:
                # Update booking
                pass

# ✅ AFTER: Early returns
if not booking:
    return error_response("Booking not found")
if booking.user_id != user.id:
    return error_response("Unauthorized")
if booking.status != "PENDING":
    return error_response("Cannot reschedule completed booking")
if new_date <= current_date:
    return error_response("Date must be in the future")

# Update booking
```

---

### **Step 7: Commit & Document** 📝
**Time**: 5% of total development time

**Actions**:
1. **Write Descriptive Commit Messages**
   ```bash
   # ✅ GOOD
   git commit -m "feat: implement reschedule booking in BookingAgent
   
   - Add _reschedule_booking() method with date validation
   - Add provider availability check for new date
   - Add unit tests for happy path and edge cases
   - Update booking status and send confirmation
   
   Closes #123"
   
   # ❌ BAD
   git commit -m "update booking agent"
   ```

2. **Update Task List**
   - Mark completed tasks
   - Update progress
   - Document any blockers

3. **Create Summary Document**
   - What was implemented
   - What tests were added
   - What's still pending

4. **Push to Feature Branch**
   ```bash
   git push origin feature/booking-agent-reschedule
   ```

---

## 🏗️ **LAYERED ARCHITECTURE PATTERN**

Follow this structure for all features:

```
┌─────────────────────────────────────┐
│  API Layer (Routes)                 │  ← HTTP handling only
│  - Request validation               │
│  - Response formatting              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Service Layer (Business Logic)     │  ← Core logic here
│  - Business rules                   │
│  - Orchestration                    │
│  - Error handling                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Repository Layer (Data Access)     │  ← Database operations
│  - CRUD operations                  │
│  - Query building                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Database (MySQL)                   │
└─────────────────────────────────────┘
```

**Example**:
```python
# ❌ BAD: Business logic in route
@router.post("/bookings/reschedule")
async def reschedule_booking(request: RescheduleRequest):
    # Don't put business logic here!
    booking = db.query(Booking).filter_by(id=request.booking_id).first()
    if booking.status == "COMPLETED":
        raise HTTPException(400, "Cannot reschedule")
    # ... more logic

# ✅ GOOD: Thin controller
@router.post("/bookings/reschedule")
async def reschedule_booking(request: RescheduleRequest):
    result = await booking_service.reschedule_booking(
        booking_id=request.booking_id,
        new_date=request.new_date,
        user=current_user
    )
    return result
```

---

## 🚫 **COMMON PITFALLS TO AVOID**

### **1. Assuming Field Names**
```python
# ❌ BAD
booking.total  # Might be total_amount!

# ✅ GOOD
# Check model first, then use correct field
booking.total_amount
```

### **2. Not Checking Return Types**
```python
# ❌ BAD
result = service.create_booking(...)
booking_id = result.id  # What if result is a dict?

# ✅ GOOD
result = service.create_booking(...)  # Returns BookingResponse
booking_id = result.booking_id  # Correct field
```

### **3. Circular Imports**
```python
# ❌ BAD: Module-level import
from backend.src.services.slot_filling_service import run_graph

# ✅ GOOD: Import inside function
def process():
    from backend.src.services.slot_filling_service import run_graph
    return run_graph()
```

### **4. Not Handling Errors**
```python
# ❌ BAD
booking = await db.get(Booking, booking_id)
booking.status = "CANCELLED"  # What if booking is None?

# ✅ GOOD
booking = await db.get(Booking, booking_id)
if not booking:
    raise BookingNotFoundError(f"Booking {booking_id} not found")
booking.status = "CANCELLED"
```

### **5. Writing Tests After Implementation**
```python
# ❌ BAD: Write code first, tests later (often incomplete)

# ✅ GOOD: Write tests first (TDD)
# 1. Write test
# 2. Run test (fails)
# 3. Write code
# 4. Run test (passes)
# 5. Refactor
```

---

## ✅ **CHECKLIST FOR EVERY FEATURE**

Before marking a feature as complete, verify:

- [ ] **Research Done**
  - [ ] Checked latest documentation (Context7)
  - [ ] Searched existing codebase for patterns
  - [ ] Verified database schema
  - [ ] Confirmed all API signatures

- [ ] **Planning Done**
  - [ ] Written implementation plan
  - [ ] Identified all dependencies
  - [ ] Listed edge cases
  - [ ] Designed data flow

- [ ] **Tests Written**
  - [ ] Unit tests for happy path
  - [ ] Unit tests for edge cases
  - [ ] Integration tests (if needed)
  - [ ] All tests passing

- [ ] **Implementation Done**
  - [ ] Code follows existing patterns
  - [ ] Type hints added
  - [ ] Comments added for complex logic
  - [ ] Error handling implemented

- [ ] **Quality Checks**
  - [ ] Code reviewed (self-review)
  - [ ] No code duplication
  - [ ] No hardcoded values
  - [ ] Follows SOLID principles

- [ ] **Documentation Done**
  - [ ] Docstrings added
  - [ ] README updated (if needed)
  - [ ] Task list updated
  - [ ] Summary document created

- [ ] **Git Done**
  - [ ] Descriptive commit message
  - [ ] Pushed to feature branch
  - [ ] No merge conflicts

---

## 🎯 **SUMMARY: THE PERFECT WORKFLOW**

```
1. Research (30%) → Understand everything first
2. Plan (15%) → Design before coding
3. Test First (20%) → Write tests before code (TDD)
4. Implement (30%) → Small chunks, one at a time
5. Test (15%) → Run all tests, check coverage
6. Review (10%) → Self-review and refactor
7. Commit (5%) → Document and push
```

**Key Principles**:
- ✅ **Never assume** - Always verify
- ✅ **Test first** - TDD prevents bugs
- ✅ **Small chunks** - Easier to debug
- ✅ **Follow patterns** - Consistency matters
- ✅ **Document everything** - Future you will thank you

**Result**: Fewer bugs, less rework, faster development! 🚀

