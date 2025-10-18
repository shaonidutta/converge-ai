# Phase 10: Multi-Agent System API Guide

**Date:** October 18, 2025  
**Status:** Complete  
**Purpose:** Developer guide for using and extending the multi-agent system

---

## 📚 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Using CoordinatorAgent](#using-coordinatoragent)
3. [Adding New Agents](#adding-new-agents)
4. [Defining Agent Dependencies](#defining-agent-dependencies)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Best Practices](#best-practices)
7. [Testing Guide](#testing-guide)
8. [Performance Optimization](#performance-optimization)

---

## 🚀 QUICK START

### **Basic Usage**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.agents.coordinator.coordinator_agent import CoordinatorAgent
from src.core.models import User

# Create coordinator agent
coordinator = CoordinatorAgent(db=db_session)

# Execute user message
result = await coordinator.execute(
    message="Tell me about AC service",
    user=user,
    session_id="session-123"
)

# Access response
print(result["response"])
print(result["agent_used"])
print(result["action_taken"])
```

### **Multi-Intent Request**

```python
# User asks multiple questions
result = await coordinator.execute(
    message="Tell me about AC service AND show cancellation policy",
    user=user,
    session_id="session-123"
)

# Check provenance
for entry in result["provenance"]:
    print(f"{entry['agent']}: {entry['contribution']}")
    print(f"  Execution time: {entry['execution_time_ms']}ms")
    print(f"  Success: {entry['success']}")
```

---

## 🎯 USING COORDINATORAGENT

### **1. Initialization**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.agents.coordinator.coordinator_agent import CoordinatorAgent

async def create_coordinator(db: AsyncSession) -> CoordinatorAgent:
    """
    Create and initialize CoordinatorAgent
    
    The coordinator automatically initializes:
    - IntentClassifier
    - All 7 specialist agents
    - Agent execution graph
    """
    coordinator = CoordinatorAgent(db=db)
    return coordinator
```

### **2. Execute Method**

```python
async def execute(
    self,
    message: str,
    user: User,
    session_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute user message through multi-agent system
    
    Args:
        message: User's natural language message
        user: User object (for personalization)
        session_id: Conversation session ID
        context: Optional conversation context
    
    Returns:
        {
            "response": str,              # Final response to user
            "agent_used": str,            # Primary agent used
            "action_taken": str,          # Action performed
            "provenance": List[Dict],     # Agent contributions
            "metadata": Dict              # Additional metadata
        }
    """
    pass
```

### **3. Response Structure**

```python
# Single intent response
{
    "response": "AC service costs ₹500 for basic cleaning",
    "agent_used": "service",
    "action_taken": "service_info_retrieved",
    "metadata": {
        "service_id": 1,
        "intent": "service_inquiry",
        "confidence": 0.92
    }
}

# Multi-intent response
{
    "response": "**Service**: AC service costs ₹500...\n\n**Policy**: Cancellation policy...",
    "agent_used": "multi_agent",
    "action_taken": "multi_intent_handled",
    "provenance": [
        {
            "agent": "service",
            "contribution": "AC service costs ₹500...",
            "action_taken": "service_info_retrieved",
            "order": 1,
            "execution_time_ms": 150,
            "success": True
        },
        {
            "agent": "policy",
            "contribution": "Cancellation policy...",
            "action_taken": "policy_retrieved",
            "order": 2,
            "execution_time_ms": 200,
            "success": True
        }
    ],
    "metadata": {
        "intent_count": 2,
        "intents_processed": ["service_inquiry", "policy_inquiry"],
        "agents_used": ["service", "policy"],
        "execution_plan": "parallel",
        "combined_metadata": {...}
    }
}
```

---

## ➕ ADDING NEW AGENTS

### **Step 1: Create Agent Class**

```python
# src/agents/my_agent/my_agent.py

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.models import User

class MyAgent:
    """
    Custom agent for specific functionality
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize any dependencies
    
    async def execute(
        self,
        intent_result: Dict[str, Any],
        user: User,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute agent logic
        
        Args:
            intent_result: Intent classification result
            user: User object
            session_id: Session ID
            context: Optional context from previous agents
        
        Returns:
            {
                "response": str,
                "action_taken": str,
                "agent_used": str,
                "metadata": Dict
            }
        """
        try:
            # Your agent logic here
            result = await self._process_request(intent_result, user)
            
            return {
                "response": result,
                "action_taken": "my_action",
                "agent_used": "my_agent",
                "metadata": {"key": "value"}
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "action_taken": "error",
                "agent_used": "my_agent",
                "metadata": {"error": str(e)}
            }
    
    async def _process_request(
        self,
        intent_result: Dict[str, Any],
        user: User
    ) -> str:
        """
        Internal processing logic
        """
        # Implement your logic
        pass
```

### **Step 2: Register Agent in CoordinatorAgent**

```python
# src/agents/coordinator/coordinator_agent.py

from src.agents.my_agent.my_agent import MyAgent

class CoordinatorAgent:
    def __init__(self, db: AsyncSession):
        # ... existing code ...
        
        # Add your agent
        self.my_agent = MyAgent(db=db)
    
    async def _route_to_agent(
        self,
        intent_result: IntentResult,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """Route to appropriate agent"""
        intent = intent_result.intent
        
        # Add routing logic
        if intent in ["my_intent_1", "my_intent_2"]:
            return await self.my_agent.execute(
                intent_result=intent_result.model_dump(),
                user=user,
                session_id=session_id
            )
        
        # ... existing routing logic ...
```

### **Step 3: Add Intent Patterns**

```python
# src/nlp/intent/patterns.py

INTENT_PATTERNS = {
    # ... existing patterns ...
    
    "my_intent_1": [
        r"my custom pattern",
        r"another pattern",
    ],
}
```

---

## 🔗 DEFINING AGENT DEPENDENCIES

### **Add to Dependency Map**

```python
# src/graphs/agent_execution_graph.py

INTENT_DEPENDENCIES = {
    # Existing dependencies
    "booking_modify": ["booking_create", "booking_status"],
    "booking_reschedule": ["booking_create", "booking_status"],
    "complaint": ["booking_status"],
    "booking_cancel": ["booking_status"],
    
    # Add your dependencies
    "my_dependent_intent": ["my_required_intent"],
}
```

### **Dependency Rules**

1. **Independent Intents**: Execute in parallel
   - No dependencies
   - Can run concurrently
   - Example: `service_inquiry`, `policy_inquiry`

2. **Dependent Intents**: Execute sequentially
   - Requires another intent's result
   - Runs after dependency
   - Example: `complaint` depends on `booking_status`

3. **Context Passing**: Dependent agents receive context
   ```python
   async def execute(
       self,
       intent_result: Dict[str, Any],
       user: User,
       session_id: str,
       context: Optional[Dict[str, Any]] = None  # Context from previous agents
   ) -> Dict[str, Any]:
       if context:
           # Use context from previous agent
           booking_id = context.get("booking_id")
   ```

---

## 🛡️ ERROR HANDLING PATTERNS

### **Pattern 1: Try-Catch in Agent**

```python
async def execute(self, intent_result, user, session_id):
    try:
        result = await self._process_request(intent_result, user)
        return {
            "response": result,
            "action_taken": "success",
            "agent_used": "my_agent",
            "metadata": {}
        }
    except ValueError as e:
        # Handle specific errors
        return {
            "response": f"Invalid input: {str(e)}",
            "action_taken": "validation_error",
            "agent_used": "my_agent",
            "metadata": {"error": str(e)}
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error in MyAgent: {str(e)}")
        return {
            "response": "I encountered an error processing your request",
            "action_taken": "error",
            "agent_used": "my_agent",
            "metadata": {"error": str(e)}
        }
```

### **Pattern 2: Graceful Degradation**

```python
async def execute(self, intent_result, user, session_id):
    try:
        # Try primary method
        result = await self._primary_method(intent_result, user)
    except Exception as e:
        logger.warning(f"Primary method failed: {str(e)}")
        try:
            # Fallback to secondary method
            result = await self._fallback_method(intent_result, user)
        except Exception as e2:
            logger.error(f"Fallback also failed: {str(e2)}")
            result = "I'm having trouble processing your request"
    
    return {
        "response": result,
        "action_taken": "processed",
        "agent_used": "my_agent",
        "metadata": {}
    }
```

### **Pattern 3: Timeout Protection**

```python
import asyncio

async def execute(self, intent_result, user, session_id):
    try:
        # Set timeout for long-running operations
        result = await asyncio.wait_for(
            self._long_running_operation(intent_result, user),
            timeout=10.0  # 10 seconds
        )
        return {
            "response": result,
            "action_taken": "success",
            "agent_used": "my_agent",
            "metadata": {}
        }
    except asyncio.TimeoutError:
        logger.warning("Operation timed out")
        return {
            "response": "Request is taking longer than expected",
            "action_taken": "timeout",
            "agent_used": "my_agent",
            "metadata": {"timeout": True}
        }
```

---

## ✅ BEST PRACTICES

### **1. Agent Design**

```python
# ✅ DO: Keep agents focused on single responsibility
class ServiceAgent:
    """Handles service discovery and information"""
    pass

# ❌ DON'T: Create agents that do too much
class EverythingAgent:
    """Handles services, bookings, complaints, etc."""
    pass
```

### **2. Response Format**

```python
# ✅ DO: Always return consistent structure
return {
    "response": "User-friendly message",
    "action_taken": "specific_action",
    "agent_used": "agent_name",
    "metadata": {"key": "value"}
}

# ❌ DON'T: Return inconsistent structures
return "Just a string"  # Missing metadata
```

### **3. Error Messages**

```python
# ✅ DO: Provide user-friendly error messages
return {
    "response": "I couldn't find that booking. Please check the booking ID.",
    "action_taken": "booking_not_found",
    "agent_used": "booking",
    "metadata": {"error": "Booking not found"}
}

# ❌ DON'T: Expose technical errors to users
return {
    "response": "SQLAlchemy.exc.NoResultFound: No row was found",
    "action_taken": "error",
    "agent_used": "booking",
    "metadata": {}
}
```

### **4. Async Operations**

```python
# ✅ DO: Use async/await for I/O operations
async def execute(self, intent_result, user, session_id):
    result = await self.db.execute(query)
    return result

# ❌ DON'T: Use blocking operations
def execute(self, intent_result, user, session_id):
    result = requests.get(url)  # Blocking!
    return result
```

### **5. Logging**

```python
# ✅ DO: Log important events
logger.info(f"Processing {intent} for user {user.id}")
logger.error(f"Error in agent: {str(e)}")

# ❌ DON'T: Log sensitive information
logger.info(f"User password: {user.password}")  # Never!
```

---

## 🧪 TESTING GUIDE

### **Unit Test Template**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_my_agent_success():
    """Test successful agent execution"""
    # Setup
    db_session = AsyncMock()
    agent = MyAgent(db=db_session)
    
    intent_result = {
        "intent": "my_intent",
        "confidence": 0.9,
        "entities": {}
    }
    user = MagicMock()
    user.id = 1
    
    # Execute
    result = await agent.execute(
        intent_result=intent_result,
        user=user,
        session_id="test-session"
    )
    
    # Assert
    assert result["response"] is not None
    assert result["agent_used"] == "my_agent"
    assert result["action_taken"] == "success"
```

### **Integration Test Template**

```python
@pytest.mark.asyncio
async def test_coordinator_with_my_agent():
    """Test coordinator routing to my agent"""
    # Setup
    coordinator = CoordinatorAgent(db=db_session)
    
    # Mock intent classifier
    with patch.object(coordinator.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="my_intent",
                confidence=0.9,
                intents=[IntentResult(intent="my_intent", confidence=0.9, entities={})]
            ),
            "pattern_match"
        )
        
        # Execute
        result = await coordinator.execute(
            message="Test message",
            user=user,
            session_id="test-session"
        )
        
        # Assert
        assert result["agent_used"] == "my_agent"
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### **1. Use Parallel Execution**

```python
# ✅ DO: Let independent intents run in parallel
# The system automatically detects and parallelizes

# ❌ DON'T: Force sequential execution for independent intents
```

### **2. Optimize Database Queries**

```python
# ✅ DO: Use eager loading
query = select(Booking).options(
    selectinload(Booking.items),
    selectinload(Booking.user)
)

# ❌ DON'T: Cause N+1 queries
bookings = await db.execute(select(Booking))
for booking in bookings:
    items = await db.execute(select(BookingItem).where(BookingItem.booking_id == booking.id))
```

### **3. Cache Expensive Operations**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_service_info(service_id: int) -> Dict:
    """Cache service information"""
    pass
```

### **4. Set Appropriate Timeouts**

```python
# Default timeout is 30 seconds
# Adjust based on your needs
result = await coordinator.execute(
    message="Complex query",
    user=user,
    session_id="session-123"
)

# In agent execution graph, timeout can be configured
initial_state = {
    "agent_timeout": 60,  # 60 seconds for complex operations
    ...
}
```

---

## 📝 SUMMARY

### **Key Takeaways**

1. **CoordinatorAgent** is the entry point for all user messages
2. **Specialist agents** handle specific domains (service, booking, policy, etc.)
3. **Agent Execution Graph** orchestrates multi-agent workflows
4. **Parallel execution** improves performance for independent intents
5. **Provenance tracking** provides transparency and debugging
6. **Error handling** ensures system resilience
7. **Best practices** ensure maintainability and scalability

### **Next Steps**

1. Review existing agents for patterns
2. Create your custom agent following the template
3. Add intent patterns for routing
4. Define dependencies if needed
5. Write comprehensive tests
6. Monitor performance and optimize

---

**End of API Guide**

