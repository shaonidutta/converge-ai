# Slot-Filling & LangGraph Implementation Plan

**Date:** 2025-10-09  
**Status:** IN PROGRESS  
**Architecture:** Modular LangGraph with Thin, Async, Stateless Nodes

---

## 📊 **IMPLEMENTATION STATUS**

### ✅ **COMPLETED**
- [x] Task 9.1: Dialog State Manager (Database + Service)
- [x] Task 9.2: Context-Aware Intent Classification
- [x] State Definitions (`backend/src/graphs/state.py`)
- [x] Slot-Filling Graph Structure (`backend/src/graphs/slot_filling_graph.py`)

### 🚧 **IN PROGRESS**
- [ ] Task 9.3: Question Generator Service
- [ ] Task 9.4: Entity Extractor Service
- [ ] Task 9.5: Entity Validator Service
- [ ] Task 9.6: Slot-Filling Orchestrator Service
- [ ] Task 9.7: LangGraph Integration
- [ ] Task 9.8: Chat Service Integration

### ⏭️ **PENDING**
- [ ] Task 10.1: Coordinator Agent
- [ ] Task 10.2: Booking Agent
- [ ] Task 10.3: SQL Agent
- [ ] Task 10.4-10.6: Other Specialist Agents
- [ ] Task 11: Integration Tests

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Modular LangGraph System**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODULAR LANGGRAPH SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

Graph 1: SLOT-FILLING GRAPH (Collect Information)
  Entry: User Message
    ↓
  classify_intent_node
    ↓
  check_follow_up_node
    ↓
  ┌─────────────────────────────────────┐
  │ Is Follow-Up?                       │
  ├─ YES → extract_entity_node          │
  │         ↓                            │
  │       validate_entity_node          │
  │         ↓                            │
  │       update_dialog_state_node      │
  │                                      │
  └─ NO → determine_needed_entities_node│
          ↓                              │
        generate_question_node           │
  └─────────────────────────────────────┘
    ↓
  ┌─────────────────────────────────────┐
  │ All Entities Collected?             │
  ├─ YES → Trigger Agent Execution Graph│
  └─ NO → Return Question to User       │
  └─────────────────────────────────────┘

Graph 2: AGENT EXECUTION GRAPH (Execute Actions)
  Entry: Collected Entities + Intent
    ↓
  route_to_agent_node
    ↓
  ┌─────────────────────────────────────┐
  │ Which Agent?                        │
  ├─ BookingAgent → execute_booking     │
  ├─ SQLAgent → execute_sql_query       │
  ├─ PolicyAgent → execute_rag_query    │
  └─ ... (other agents)                 │
  └─────────────────────────────────────┘
    ↓
  generate_response_node
    ↓
  Exit: Final Response

Graph 3: ERROR HANDLING GRAPH (Handle Failures)
  Entry: Error Context
    ↓
  classify_error_node
    ↓
  generate_error_response_node
    ↓
  Exit: User-Friendly Error Message
```

---

## 📁 **FILE STRUCTURE**

```
backend/
├── src/
│   ├── graphs/
│   │   ├── __init__.py
│   │   ├── state.py                      ✅ CREATED
│   │   ├── slot_filling_graph.py         ✅ CREATED
│   │   ├── agent_execution_graph.py      ⏭️ TODO
│   │   └── error_handling_graph.py       ⏭️ TODO
│   │
│   ├── services/
│   │   ├── dialog_state_manager.py       ✅ COMPLETED
│   │   ├── question_generator.py         ⏭️ TODO (Task 9.3)
│   │   ├── entity_extractor.py           ⏭️ TODO (Task 9.4)
│   │   ├── entity_validator.py           ⏭️ TODO (Task 9.5)
│   │   ├── slot_filling_service.py       ⏭️ TODO (Task 9.6)
│   │   └── chat_service.py               🚧 NEEDS INTEGRATION
│   │
│   ├── nlp/
│   │   └── intent/
│   │       ├── classifier.py             ✅ COMPLETED
│   │       ├── config.py                 ✅ COMPLETED
│   │       └── patterns.py               ✅ COMPLETED
│   │
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py                 ⏭️ TODO
│       ├── coordinator_agent.py          ⏭️ TODO
│       ├── booking_agent.py              ⏭️ TODO
│       ├── sql_agent.py                  ⏭️ TODO
│       └── ... (other agents)
│
└── tests/
    ├── test_dialog_state_manager.py      ✅ COMPLETED
    ├── test_context_aware_intent.py      ✅ COMPLETED
    ├── test_question_generator.py        ⏭️ TODO
    ├── test_entity_extractor.py          ⏭️ TODO
    ├── test_entity_validator.py          ⏭️ TODO
    ├── test_slot_filling_graph.py        ⏭️ TODO
    └── test_slot_filling_integration.py  ⏭️ TODO
```

---

## 🔄 **SLOT-FILLING GRAPH FLOW**

### **Nodes (Thin, Async, Stateless)**

1. **classify_intent_node**
   - Calls: `IntentClassifier.classify()`
   - Input: `current_message`, `conversation_history`, `dialog_state`
   - Output: `intent_result`, `primary_intent`, `confidence`
   - Error Handling: Try/catch → route to `handle_error_node`

2. **check_follow_up_node**
   - Calls: `DialogStateManager.is_follow_up_response()`
   - Input: `current_message`, `session_id`
   - Output: `is_follow_up`, `follow_up_confidence`, `expected_entity`
   - Error Handling: Try/catch → route to `handle_error_node`

3. **extract_entity_node**
   - Calls: `EntityExtractor.extract_from_follow_up()`
   - Input: `current_message`, `expected_entity`, `context`
   - Output: `extracted_entity` (type, value, normalized_value)
   - Error Handling: Try/catch → route to `handle_error_node`

4. **validate_entity_node**
   - Calls: `EntityValidator.validate()`
   - Input: `extracted_entity`, `context`
   - Output: `validation_result` (is_valid, normalized_value, error_message)
   - Error Handling: Try/catch → route to `handle_error_node`

5. **update_dialog_state_node**
   - Calls: `DialogStateManager.add_entity()`, `remove_needed_entity()`
   - Input: `validation_result`, `extracted_entity`
   - Output: Updated `collected_entities`, `needed_entities`
   - Error Handling: Try/catch → route to `handle_error_node`

6. **determine_needed_entities_node**
   - Logic: Compare `collected_entities` vs `required_entities` from `INTENT_CONFIGS`
   - Input: `primary_intent`, `collected_entities`
   - Output: `needed_entities` list
   - Error Handling: Try/catch → route to `handle_error_node`

7. **generate_question_node**
   - Calls: `QuestionGenerator.generate()` or `generate_confirmation()`
   - Input: `needed_entities`, `collected_entities`, `validation_errors`
   - Output: `current_question`, `final_response`
   - Error Handling: Try/catch → route to `handle_error_node`

8. **handle_error_node**
   - Logic: Convert technical errors to user-friendly messages
   - Input: `error` object
   - Output: `final_response` (user-friendly error message)
   - Error Handling: Try/catch with fallback message

### **Conditional Edges**

1. **should_route_to_error**
   - Check: `state.get('error')` exists?
   - Routes: `"error"` → `handle_error_node`, `"continue"` → next node

2. **is_follow_up_response**
   - Check: `is_follow_up == True` and `follow_up_confidence > 0.6`?
   - Routes: `"follow_up"` → `extract_entity_node`, `"new_intent"` → `determine_needed_entities_node`

3. **is_validation_successful**
   - Check: `validation_result.is_valid == True`?
   - Routes: `"valid"` → `update_dialog_state_node`, `"invalid"` → `generate_question_node`

4. **are_all_entities_collected**
   - Check: `needed_entities` list is empty?
   - Routes: `"all_collected"` → `generate_question_node` (confirmation), `"more_needed"` → `generate_question_node` (next entity)

5. **should_trigger_agent_execution**
   - Check: User confirmed? OR All entities collected?
   - Routes: `"execute_agent"` → END (trigger Graph 2), `"ask_question"` → END (return question)

---

## 🎯 **NEXT STEPS (Priority Order)**

### **Step 1: Implement Core Services (Tasks 9.3-9.5)**

#### **Task 9.3: Question Generator Service** 🔴 CRITICAL
- **File:** `backend/src/services/question_generator.py`
- **Approach:** Template-based (MVP)
- **Key Methods:**
  - `generate(entity_type, intent, collected_entities)` → question string
  - `generate_confirmation(intent, collected_entities)` → confirmation message
- **Estimated Time:** 2-3 hours

#### **Task 9.4: Entity Extractor Service** 🔴 CRITICAL
- **File:** `backend/src/services/entity_extractor.py`
- **Approach:** Pattern matching (fast path) + LLM (fallback)
- **Key Methods:**
  - `extract_from_follow_up(message, expected_entity, context)` → EntityExtractionResult
  - `_extract_with_patterns()` → pattern-based extraction
  - `_extract_with_llm()` → LLM-based extraction
- **Estimated Time:** 3-4 hours

#### **Task 9.5: Entity Validator Service** 🔴 CRITICAL
- **File:** `backend/src/services/entity_validator.py`
- **Approach:** Business rule validation + DB checks
- **Key Methods:**
  - `validate(entity_type, value, context)` → ValidationResult
  - `_validate_date()`, `_validate_time()`, `_validate_location()`, etc.
- **Estimated Time:** 2-3 hours

---

### **Step 2: Create Slot-Filling Orchestrator (Task 9.6)**

#### **Task 9.6: Slot-Filling Service** 🔴 CRITICAL
- **File:** `backend/src/services/slot_filling_service.py`
- **Purpose:** High-level orchestrator that uses the LangGraph
- **Key Methods:**
  - `process_message(message, session_id, user)` → SlotFillingResponse
  - Initializes state, runs graph, returns response
- **Estimated Time:** 4-5 hours

---

### **Step 3: Integrate into Chat Service (Task 9.8)**

#### **Task 9.8: Chat Service Integration** 🟠 HIGH
- **File:** `backend/src/services/chat_service.py`
- **Changes:**
  - Replace placeholder in `_get_ai_response()`
  - Initialize services (classifier, dialog_manager, etc.)
  - Call `run_slot_filling_graph()`
  - Store response with metadata
- **Estimated Time:** 3-4 hours

---

## 📝 **DESIGN DECISIONS**

### **1. Modular Graphs**
✅ **Decision:** Separate graphs for slot-filling vs agent execution  
**Rationale:** Better separation of concerns, easier testing, reusable components

### **2. State Structure**
✅ **Decision:** Comprehensive `ConversationState` TypedDict  
**Rationale:** Context-aware, serializable, contains all info for stateless nodes

### **3. Node Design**
✅ **Decision:** Thin, async, stateless nodes  
**Rationale:** Easy to test, no side effects, pure functions

### **4. Error Handling**
✅ **Decision:** Hybrid (try/catch + dedicated error node)  
**Rationale:** Graceful degradation, user-friendly error messages

### **5. Service Injection**
✅ **Decision:** Inject services via lambda closures  
**Rationale:** Nodes remain stateless, services are reusable

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
- Test each service independently
- Mock dependencies
- Test edge cases (invalid inputs, errors)

### **Integration Tests**
- Test complete slot-filling flow
- Test graph execution
- Test error handling

### **End-to-End Tests**
- Test through chat API
- Test multi-turn conversations
- Test context switching

---

## 📊 **ESTIMATED TIMELINE**

| Task | Priority | Estimated Time | Status |
|------|----------|----------------|--------|
| Task 9.3: Question Generator | 🔴 CRITICAL | 2-3 hours | ⏭️ TODO |
| Task 9.4: Entity Extractor | 🔴 CRITICAL | 3-4 hours | ⏭️ TODO |
| Task 9.5: Entity Validator | 🔴 CRITICAL | 2-3 hours | ⏭️ TODO |
| Task 9.6: Slot-Filling Service | 🔴 CRITICAL | 4-5 hours | ⏭️ TODO |
| Task 9.7: LangGraph Setup | 🟠 HIGH | 2-3 hours | 🚧 IN PROGRESS |
| Task 9.8: Chat Service Integration | 🟠 HIGH | 3-4 hours | ⏭️ TODO |
| **TOTAL** | | **16-22 hours** | |

---

## 🚀 **READY TO PROCEED**

**Next Action:** Implement Task 9.3 (Question Generator Service)

**Command to start:**
```bash
# Create the service file
touch backend/src/services/question_generator.py

# Create the test file
touch backend/tests/test_question_generator.py
```

---

**Questions or concerns? Let's discuss before proceeding!** 🎯

