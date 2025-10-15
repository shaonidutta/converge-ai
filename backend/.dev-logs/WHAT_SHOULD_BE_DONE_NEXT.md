# What Should Be Done Next - Based on Previous Planning

## Date: 2025-10-14

---

## 📊 **CURRENT STATUS RECAP**

### **✅ What's Complete**
1. ✅ **Phase 1-3**: Project setup, database, core configuration
2. ✅ **Task 9**: Intent classification and slot-filling (LangGraph)
3. ✅ **Task 9.8**: Chat service integration with slot-filling
4. ✅ **BookingAgent**: Partially complete (create, validate, cancel)
5. ✅ **Rate Card Descriptions**: All 154 rate cards have descriptions
6. ✅ **Integration Tests**: Booking creation verified

### **⏳ What's In Progress**
- BookingAgent: Reschedule and modify methods (placeholders)

### **❌ What's Pending**
- 6 specialist agents (CancellationAgent, ComplaintAgent, PolicyAgent, ServiceAgent, SQLAgent, CoordinatorAgent)
- LangGraph multi-agent orchestration
- RAG pipeline for PolicyAgent
- Customer and Ops APIs
- Authentication & Authorization
- Background task queue (Celery)

---

## 🎯 **RECOMMENDED NEXT STEPS (Priority Order)**

Based on our previous discussions and the implementation roadmap, here's what should be done next:

---

## **PHASE 1: Complete Agent Execution (Task 10)**

### **Priority 1: Complete BookingAgent** ⚡ HIGH PRIORITY
**Estimated Time**: 1-2 days

**Tasks**:
1. Implement `_reschedule_booking()` method
   - Validate new date/time
   - Check provider availability
   - Update booking record
   - Send confirmation

2. Implement `_modify_booking()` method
   - Allow special instructions update
   - Allow address change (if not started)
   - Validate modifications
   - Update booking record

3. Add unit tests for new methods

**Why First**: BookingAgent is already 70% complete and is the most critical agent for customer bookings.

---

### **Priority 2: Implement ServiceAgent** ⚡ HIGH PRIORITY
**Estimated Time**: 2-3 days

**Purpose**: Help customers discover services, get pricing, and check availability

**Tasks**:
1. Create `backend/src/agents/service/service_agent.py`
2. Implement methods:
   - `_get_service_info()` - Retrieve service details with descriptions
   - `_recommend_services()` - Suggest services based on user needs
   - `_calculate_price()` - Calculate total with discounts
   - `_check_availability()` - Check pincode coverage
   - `_compare_tiers()` - Compare Basic/Standard/Premium

3. Integration with:
   - RateCard model (with new descriptions)
   - Category/Subcategory models
   - Provider availability check

4. Create tests

**Why Second**: Customers need to discover services before booking. This is the entry point of the customer journey.

---

### **Priority 3: Implement PolicyAgent (RAG)** ⚡ HIGH PRIORITY
**Estimated Time**: 3-4 days

**Purpose**: Answer policy questions using RAG (Retrieval-Augmented Generation)

**Tasks**:
1. **Set up Pinecone Integration**
   - Create Pinecone index
   - Configure embeddings (sentence-transformers/all-MiniLM-L6-v2)
   - Set up connection in config

2. **Ingest Policy Documents**
   - Load policy PDFs from `backend/docs/policies/`
   - Chunk documents (512 tokens with 50 token overlap)
   - Generate embeddings
   - Upload to Pinecone

3. **Create PolicyAgent**
   - `backend/src/agents/policy/policy_agent.py`
   - Implement vector search
   - Implement context retrieval
   - Generate responses with citations
   - Calculate grounding scores

4. **RAG Pipeline**
   - Create `backend/src/rag/retrieval/policy_retriever.py`
   - Create `backend/src/rag/prompts/policy_prompts.py`
   - Implement response generation with LangChain

5. Create tests

**Why Third**: Customer support queries about policies, refunds, cancellations are common. RAG ensures accurate, grounded responses.

---

### **Priority 4: Implement CoordinatorAgent** ⚡ HIGH PRIORITY
**Estimated Time**: 2-3 days

**Purpose**: Route intents to appropriate specialist agents and orchestrate multi-agent execution

**Tasks**:
1. Create `backend/src/agents/coordinator/coordinator_agent.py`
2. Implement methods:
   - `_route_to_agent()` - Select appropriate agent based on intent
   - `_execute_parallel()` - Run multiple agents for multi-intent queries
   - `_merge_responses()` - Combine responses from multiple agents
   - `_add_provenance()` - Track which agent answered what
   - `_handle_failure()` - Fallback logic

3. **Agent Routing Logic**:
   ```python
   intent_to_agent_map = {
       "book_service": BookingAgent,
       "cancel_booking": BookingAgent,  # or CancellationAgent
       "service_inquiry": ServiceAgent,
       "policy_question": PolicyAgent,
       "complaint": ComplaintAgent,
       "general_query": SQLAgent or PolicyAgent
   }
   ```

4. Create LangGraph workflow for agent orchestration

5. Create tests

**Why Fourth**: Once we have 3-4 specialist agents, we need the coordinator to route requests properly.

---

### **Priority 5: Implement CancellationAgent** 🔶 MEDIUM PRIORITY
**Estimated Time**: 1-2 days

**Purpose**: Handle booking cancellations with policy checks and refund calculation

**Tasks**:
1. Create `backend/src/agents/cancellation/cancellation_agent.py`
2. Implement methods:
   - `_lookup_booking()` - Find booking by ID
   - `_check_cancellation_policy()` - Verify refund eligibility
   - `_calculate_refund()` - Calculate refund based on policy
   - `_cancel_booking()` - Execute cancellation
   - `_send_confirmation()` - Send cancellation confirmation

3. **Policy Rules**:
   - Full refund: >24 hours before scheduled time
   - 50% refund: 12-24 hours before
   - No refund: <12 hours before
   - Handle partial cancellations (multi-item bookings)

4. Create tests

**Why Fifth**: Can use BookingAgent's cancel method temporarily, but dedicated agent provides better policy handling.

---

### **Priority 6: Implement ComplaintAgent** 🔶 MEDIUM PRIORITY
**Estimated Time**: 2-3 days

**Purpose**: Handle customer complaints with priority scoring and routing

**Tasks**:
1. Create `backend/src/agents/complaint/complaint_agent.py`
2. Implement methods:
   - `_create_complaint()` - Create complaint record
   - `_calculate_priority()` - Score urgency (urgent/high/medium/low)
   - `_route_complaint()` - Route to appropriate department
   - `_update_complaint()` - Update status
   - `_escalate_complaint()` - Escalate if needed

3. **Priority Scoring**:
   - Urgent: Safety issues, service not started
   - High: Quality issues, delays
   - Medium: Minor issues
   - Low: General feedback

4. Integration with PriorityQueue table

5. Create tests

**Why Sixth**: Important for customer satisfaction but not blocking the booking flow.

---

### **Priority 7: Implement SQLAgent** 🔷 LOW PRIORITY
**Estimated Time**: 3-4 days

**Purpose**: Natural language to SQL queries (with strict security)

**Tasks**:
1. Create `backend/src/agents/sql/sql_agent.py`
2. Implement methods:
   - `_parse_nl_to_sql()` - Convert natural language to SQL
   - `_validate_query()` - Security validation
   - `_parameterize_query()` - Convert to parameterized query
   - `_execute_query()` - Execute with timeout
   - `_format_results()` - Format for user

3. **Security Requirements**:
   - Only SELECT queries
   - No DELETE/TRUNCATE/DROP
   - Parameterized queries only
   - 5-second timeout
   - Table whitelist
   - Column whitelist for sensitive data

4. Create tests

**Why Seventh**: Nice to have for analytics but not critical for core functionality.

---

## **PHASE 2: API Development (Task 11)**

### **Priority 8: Customer Chat API** ⚡ HIGH PRIORITY
**Estimated Time**: 2-3 days

**Tasks**:
1. Create `backend/src/api/v1/endpoints/chat.py`
2. Implement endpoints:
   - `POST /api/v1/chat/message` - Send message
   - `GET /api/v1/chat/history` - Get chat history
   - `GET /api/v1/chat/sessions` - List sessions
   - `DELETE /api/v1/chat/sessions/{session_id}` - Delete session

3. Add streaming support (SSE) for real-time responses

4. Add rate limiting (10 requests/minute per user)

5. Create API tests

**Why Eighth**: Once agents are ready, we need APIs for frontend integration.

---

### **Priority 9: Customer Booking APIs** ⚡ HIGH PRIORITY
**Estimated Time**: 2-3 days

**Tasks**:
1. Create `backend/src/api/v1/endpoints/bookings.py`
2. Implement endpoints:
   - `POST /api/v1/bookings` - Create booking
   - `GET /api/v1/bookings` - List user bookings
   - `GET /api/v1/bookings/{id}` - Get booking details
   - `PUT /api/v1/bookings/{id}/cancel` - Cancel booking
   - `PUT /api/v1/bookings/{id}/reschedule` - Reschedule booking

3. Add validation and error handling

4. Create API tests

---

### **Priority 10: Operations APIs** 🔶 MEDIUM PRIORITY
**Estimated Time**: 3-4 days

**Tasks**:
1. Create `backend/src/api/v1/endpoints/ops/`
2. Implement endpoints:
   - Priority queue management
   - Complaint management
   - Analytics and insights
   - Provider management
   - Booking management (ops view)

3. Add RBAC (Role-Based Access Control)

4. Create API tests

---

## **PHASE 3: Authentication & Authorization (Task 4)**

### **Priority 11: JWT Authentication** ⚡ HIGH PRIORITY
**Estimated Time**: 2-3 days

**Tasks**:
1. Implement JWT token generation and validation
2. Create login/logout endpoints
3. Add password hashing (bcrypt)
4. Implement refresh token logic
5. Add authentication middleware
6. Create auth tests

---

### **Priority 12: RBAC Implementation** 🔶 MEDIUM PRIORITY
**Estimated Time**: 2-3 days

**Tasks**:
1. Implement permission checking middleware
2. Add role-based route protection
3. Create permission decorators
4. Add RBAC tests

---

## **PHASE 4: Background Tasks (Task 16)**

### **Priority 13: Celery Setup** 🔶 MEDIUM PRIORITY
**Estimated Time**: 2-3 days

**Tasks**:
1. Set up Celery with Redis
2. Create task definitions:
   - Send email
   - Send SMS
   - Process complaint escalation
   - Generate analytics reports
   - Cleanup old sessions
   - Send booking reminders

3. Set up Celery Beat for scheduled tasks

4. Create task tests

---

## 📋 **SUMMARY: RECOMMENDED EXECUTION ORDER**

### **Week 1-2: Core Agents**
1. ✅ Complete BookingAgent (1-2 days)
2. ✅ Implement ServiceAgent (2-3 days)
3. ✅ Implement PolicyAgent with RAG (3-4 days)

### **Week 3: Agent Orchestration**
4. ✅ Implement CoordinatorAgent (2-3 days)
5. ✅ Implement CancellationAgent (1-2 days)
6. ✅ Implement ComplaintAgent (2-3 days)

### **Week 4: APIs**
7. ✅ Customer Chat API (2-3 days)
8. ✅ Customer Booking APIs (2-3 days)

### **Week 5: Auth & Background Tasks**
9. ✅ JWT Authentication (2-3 days)
10. ✅ Celery Setup (2-3 days)

### **Week 6: Polish & Testing**
11. ✅ Operations APIs (3-4 days)
12. ✅ RBAC Implementation (2-3 days)
13. ✅ SQLAgent (if time permits)

---

## 🎯 **IMMEDIATE NEXT TASK**

**Start with**: Complete BookingAgent (`_reschedule_booking()` and `_modify_booking()` methods)

**Reason**: 
- Already 70% complete
- Critical for customer bookings
- Quick win (1-2 days)
- Builds momentum for other agents

**After that**: Implement ServiceAgent (customer service discovery)

---

## 📝 **CONCLUSION**

Based on our previous planning and the implementation roadmap, the focus should be on:

1. **Completing the multi-agent system** (Task 10) - This is the core AI functionality
2. **Building customer-facing APIs** (Task 11) - This enables frontend integration
3. **Adding authentication** (Task 4) - This secures the application
4. **Setting up background tasks** (Task 16) - This handles async operations

The recommended order prioritizes customer value and builds incrementally from what's already complete.

