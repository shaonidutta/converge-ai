# Next Steps: CoordinatorAgent Implementation

**Date**: 2025-10-15  
**Current Status**: PolicyAgent COMPLETE ✅  
**Next Priority**: CoordinatorAgent (Orchestration Layer)  
**Branch**: feature/coordinator-agent

---

## 🎯 **OBJECTIVE**

Implement the **CoordinatorAgent** - the orchestration layer that:
1. Receives user messages from the chat API
2. Classifies intent using the existing intent classification system
3. Routes requests to appropriate specialized agents
4. Manages conversation flow and context
5. Handles multi-turn conversations
6. Coordinates responses from multiple agents when needed

---

## 📊 **CURRENT SYSTEM STATUS**

### **✅ Completed Agents**

1. **PolicyAgent** (100% Complete)
   - Handles policy inquiries (cancellation, refund, booking, payment)
   - 80% pass rate, 0.93 grounding, 0.97 relevance
   - Production-ready RAG implementation

2. **ServiceAgent** (100% Complete)
   - Handles service discovery and recommendations
   - RAG-based service search
   - Integration tests passing

3. **BookingAgent** (100% Complete)
   - Handles booking creation, modification, rescheduling
   - Complex state management
   - Integration tests passing

### **⏳ Pending Agents**

1. **CoordinatorAgent** (0% - HIGH PRIORITY)
   - Orchestration layer
   - Intent routing
   - Conversation management

2. **CancellationAgent** (0% - MEDIUM PRIORITY)
   - Dedicated cancellation logic
   - Refund processing
   - Policy enforcement

3. **ComplaintAgent** (0% - MEDIUM PRIORITY)
   - Complaint handling
   - Escalation logic
   - Resolution tracking

4. **SQLAgent** (0% - LOW PRIORITY)
   - Natural language to SQL
   - Analytics queries
   - Reporting

---

## 🏗️ **COORDINATORAGENT ARCHITECTURE**

### **Core Responsibilities**

1. **Intent Classification**
   - Use existing intent classification system
   - Map intents to appropriate agents
   - Handle ambiguous intents

2. **Agent Routing**
   - Route to PolicyAgent for policy queries
   - Route to ServiceAgent for service discovery
   - Route to BookingAgent for booking operations
   - Route to CancellationAgent for cancellations
   - Route to ComplaintAgent for complaints

3. **Conversation Management**
   - Maintain conversation context
   - Handle multi-turn conversations
   - Track conversation state
   - Store conversation history

4. **Response Coordination**
   - Aggregate responses from multiple agents
   - Format responses for user
   - Handle errors gracefully
   - Provide fallback responses

### **Technical Design**

```python
class CoordinatorAgent(BaseAgent):
    """
    Orchestration agent that routes user requests to specialized agents
    """
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.policy_agent = PolicyAgent()
        self.service_agent = ServiceAgent()
        self.booking_agent = BookingAgent()
        self.conversation_manager = ConversationManager()
    
    async def execute(
        self,
        message: str,
        user: User,
        session_id: str,
        conversation_history: List[Dict] = None
    ) -> AgentResponse:
        """
        Main execution method
        
        Steps:
        1. Classify intent
        2. Extract entities
        3. Route to appropriate agent(s)
        4. Coordinate responses
        5. Update conversation history
        6. Return formatted response
        """
        pass
    
    async def _classify_intent(self, message: str) -> IntentClassification:
        """Classify user intent"""
        pass
    
    async def _route_to_agent(
        self,
        intent: str,
        entities: Dict,
        user: User,
        session_id: str
    ) -> AgentResponse:
        """Route to appropriate specialized agent"""
        pass
    
    async def _handle_multi_agent_request(
        self,
        intents: List[str],
        entities: Dict,
        user: User,
        session_id: str
    ) -> AgentResponse:
        """Handle requests requiring multiple agents"""
        pass
    
    async def _update_conversation_history(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        intent: str
    ):
        """Store conversation in database"""
        pass
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Core Coordinator (Day 1-2)**

**Tasks**:
1. Create `backend/src/agents/coordinator/coordinator_agent.py`
2. Implement intent classification integration
3. Implement basic agent routing
4. Add conversation history management
5. Create unit tests

**Deliverables**:
- CoordinatorAgent class with basic routing
- Intent classification integration
- Conversation history storage
- Unit tests (80% coverage)

### **Phase 2: Advanced Routing (Day 3)**

**Tasks**:
1. Implement multi-agent coordination
2. Add context-aware routing
3. Handle ambiguous intents
4. Implement fallback logic
5. Add error handling

**Deliverables**:
- Multi-agent request handling
- Context-aware routing logic
- Comprehensive error handling
- Integration tests

### **Phase 3: Conversation Management (Day 4)**

**Tasks**:
1. Implement conversation state tracking
2. Add multi-turn conversation support
3. Implement context carryover
4. Add conversation summarization
5. Create conversation analytics

**Deliverables**:
- Conversation state management
- Multi-turn conversation support
- Context carryover between turns
- Conversation analytics

### **Phase 4: Integration & Testing (Day 5)**

**Tasks**:
1. Integrate with chat API endpoint
2. End-to-end testing
3. Performance optimization
4. Documentation
5. Production deployment

**Deliverables**:
- Full integration with chat API
- Comprehensive test suite
- Performance benchmarks
- Complete documentation

---

## 🔧 **TECHNICAL REQUIREMENTS**

### **Dependencies**

```python
# Already available
from src.agents.policy.policy_agent import PolicyAgent
from src.agents.service.service_agent import ServiceAgent
from src.agents.booking.booking_agent import BookingAgent
from src.core.models.conversation import Conversation
from src.core.models.user import User

# Need to implement
from src.agents.coordinator.intent_classifier import IntentClassifier
from src.agents.coordinator.conversation_manager import ConversationManager
```

### **Database Schema**

**Conversations Table** (already exists):
```sql
CREATE TABLE conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(100),
    agent_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### **Intent Mapping**

```python
INTENT_TO_AGENT_MAP = {
    "policy_inquiry": PolicyAgent,
    "service_discovery": ServiceAgent,
    "booking_create": BookingAgent,
    "booking_modify": BookingAgent,
    "booking_reschedule": BookingAgent,
    "booking_cancel": CancellationAgent,  # Future
    "complaint": ComplaintAgent,  # Future
    "general_query": PolicyAgent,  # Default fallback
}
```

---

## 📊 **SUCCESS METRICS**

### **Performance Targets**

1. **Intent Classification Accuracy**: ≥95%
2. **Routing Accuracy**: ≥98%
3. **Response Time**: <3 seconds (end-to-end)
4. **Conversation Context Retention**: 100%
5. **Error Rate**: <2%

### **Quality Targets**

1. **User Satisfaction**: ≥4.5/5
2. **First Response Resolution**: ≥70%
3. **Multi-turn Success Rate**: ≥85%
4. **Fallback Rate**: <5%

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**

1. Intent classification tests
2. Agent routing tests
3. Conversation management tests
4. Error handling tests

### **Integration Tests**

1. End-to-end conversation flows
2. Multi-agent coordination tests
3. Context carryover tests
4. Error recovery tests

### **Test Scenarios**

```python
# Test 1: Simple policy query
user_message = "What is your cancellation policy?"
expected_agent = PolicyAgent
expected_intent = "policy_inquiry"

# Test 2: Service discovery
user_message = "I need a plumber in Bangalore"
expected_agent = ServiceAgent
expected_intent = "service_discovery"

# Test 3: Booking creation
user_message = "Book a plumber for tomorrow at 2 PM"
expected_agent = BookingAgent
expected_intent = "booking_create"

# Test 4: Multi-turn conversation
turn_1 = "What services do you offer?"
turn_2 = "How much does plumbing cost?"
turn_3 = "Book a plumber for tomorrow"
# Should maintain context across turns

# Test 5: Ambiguous intent
user_message = "I have a problem"
# Should ask clarifying questions
```

---

## 📝 **NEXT IMMEDIATE STEPS**

1. ✅ **Create feature branch**
   ```bash
   git checkout -b feature/coordinator-agent
   ```

2. ✅ **Create directory structure**
   ```bash
   mkdir -p backend/src/agents/coordinator
   touch backend/src/agents/coordinator/__init__.py
   touch backend/src/agents/coordinator/coordinator_agent.py
   touch backend/src/agents/coordinator/intent_classifier.py
   touch backend/src/agents/coordinator/conversation_manager.py
   ```

3. ✅ **Implement CoordinatorAgent skeleton**
   - Basic class structure
   - Intent classification integration
   - Simple routing logic

4. ✅ **Create unit tests**
   ```bash
   touch backend/tests/test_coordinator_agent.py
   ```

5. ✅ **Integrate with chat API**
   - Update `backend/src/api/v1/routes/chat.py`
   - Use CoordinatorAgent instead of direct agent calls

6. ✅ **Test end-to-end**
   - Run comprehensive tests
   - Verify all agents work through coordinator

7. ✅ **Document and commit**
   - Update documentation
   - Commit with detailed message
   - Push to feature branch

---

## 🎯 **EXPECTED OUTCOMES**

After completing CoordinatorAgent implementation:

1. ✅ **Unified Chat Interface**
   - Single entry point for all user messages
   - Automatic routing to appropriate agents
   - Seamless multi-agent coordination

2. ✅ **Improved User Experience**
   - Context-aware conversations
   - Multi-turn conversation support
   - Intelligent fallback handling

3. ✅ **Scalable Architecture**
   - Easy to add new agents
   - Centralized orchestration
   - Clean separation of concerns

4. ✅ **Production Ready**
   - Comprehensive error handling
   - Performance optimized
   - Fully tested and documented

---

## 📚 **REFERENCES**

- **PolicyAgent Implementation**: `backend/src/agents/policy/policy_agent.py`
- **ServiceAgent Implementation**: `backend/src/agents/service/service_agent.py`
- **BookingAgent Implementation**: `backend/src/agents/booking/booking_agent.py`
- **Chat API Endpoint**: `backend/src/api/v1/routes/chat.py`
- **Conversation Model**: `backend/src/core/models/conversation.py`

---

**Ready to start implementation!** 🚀

