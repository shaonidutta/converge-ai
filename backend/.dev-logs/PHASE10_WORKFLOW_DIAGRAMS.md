# Phase 10: Multi-Agent Workflow Diagrams

**Date:** October 18, 2025  
**Status:** Complete  
**Purpose:** Visual documentation of multi-agent system workflows

---

## 📊 DIAGRAM 1: Complete End-to-End Flow

```mermaid
graph TD
    A[User Message] --> B[CoordinatorAgent]
    B --> C{Intent Classification}
    
    C -->|Single Intent| D[Route to Specialist Agent]
    C -->|Multi-Intent| E[Agent Execution Graph]
    
    D --> F[Specialist Agent]
    F --> G[Return Response]
    
    E --> H[Prepare Execution Node]
    H --> I{Analyze Dependencies}
    
    I -->|Independent| J[Parallel Execution Node]
    I -->|Dependent| K[Sequential Execution Node]
    
    J --> L[Execute Agents Concurrently]
    L --> M[Merge Responses Node]
    
    K --> N[Execute Agents Sequentially]
    N --> M
    
    M --> O[Format Final Response]
    O --> P[Add Provenance Tracking]
    P --> G
    
    G --> Q[User Receives Response]
    
    style A fill:#e1f5ff
    style Q fill:#d4edda
    style E fill:#fff3cd
    style J fill:#d1ecf1
    style K fill:#f8d7da
    style M fill:#d4edda
```

---

## 📊 DIAGRAM 2: Agent Execution Graph Detail

```mermaid
graph LR
    START([Start]) --> PREPARE[Prepare Agent Execution]
    
    PREPARE --> ANALYZE{Analyze Intents}
    ANALYZE -->|Separate| INDEPENDENT[Independent Intents]
    ANALYZE -->|Separate| DEPENDENT[Dependent Intents]
    
    INDEPENDENT --> PARALLEL[Execute Parallel Agents]
    PARALLEL --> GATHER[asyncio.gather]
    GATHER --> RESULTS1[Parallel Responses]
    
    DEPENDENT --> SEQUENTIAL[Execute Sequential Agents]
    SEQUENTIAL --> CHAIN[Sequential Chain]
    CHAIN --> RESULTS2[Sequential Responses]
    
    RESULTS1 --> MERGE[Merge Responses]
    RESULTS2 --> MERGE
    
    MERGE --> FORMAT[Format Response]
    FORMAT --> PROVENANCE[Add Provenance]
    PROVENANCE --> END([End])
    
    style START fill:#28a745
    style END fill:#28a745
    style PARALLEL fill:#17a2b8
    style SEQUENTIAL fill:#ffc107
    style MERGE fill:#6f42c1
```

---

## 📊 DIAGRAM 3: Dependency Resolution

```mermaid
graph TD
    A[Multi-Intent Request] --> B{Check Dependencies}
    
    B -->|service_inquiry| C1[Independent]
    B -->|policy_inquiry| C2[Independent]
    B -->|service_discovery| C3[Independent]
    
    B -->|booking_modify| D1[Depends on booking_status]
    B -->|booking_reschedule| D2[Depends on booking_status]
    B -->|complaint| D3[Depends on booking_status]
    B -->|booking_cancel| D4[Depends on booking_status]
    
    C1 --> E[Parallel Execution Group]
    C2 --> E
    C3 --> E
    
    D1 --> F[Sequential Execution Group]
    D2 --> F
    D3 --> F
    D4 --> F
    
    E --> G[Execute Concurrently]
    F --> H[Execute in Order]
    
    G --> I[Merge Results]
    H --> I
    
    style E fill:#d1ecf1
    style F fill:#f8d7da
    style I fill:#d4edda
```

---

## 📊 DIAGRAM 4: Parallel vs Sequential Execution

```mermaid
sequenceDiagram
    participant User
    participant Coordinator
    participant Graph
    participant ServiceAgent
    participant PolicyAgent
    
    User->>Coordinator: "Tell me about AC service AND show cancellation policy"
    Coordinator->>Graph: Multi-intent detected
    Graph->>Graph: Analyze dependencies
    Graph->>Graph: Both independent → Parallel
    
    par Parallel Execution
        Graph->>ServiceAgent: Execute
        ServiceAgent-->>Graph: AC service info (150ms)
    and
        Graph->>PolicyAgent: Execute
        PolicyAgent-->>Graph: Cancellation policy (200ms)
    end
    
    Graph->>Graph: Merge responses
    Graph->>Graph: Add provenance
    Graph-->>Coordinator: Combined response (200ms total)
    Coordinator-->>User: Formatted response
    
    Note over Graph,PolicyAgent: Total time = max(150ms, 200ms) = 200ms
```

---

## 📊 DIAGRAM 5: Sequential Execution with Dependencies

```mermaid
sequenceDiagram
    participant User
    participant Coordinator
    participant Graph
    participant BookingAgent
    participant ComplaintAgent
    
    User->>Coordinator: "Show my booking AND file a complaint"
    Coordinator->>Graph: Multi-intent detected
    Graph->>Graph: Analyze dependencies
    Graph->>Graph: complaint depends on booking_status → Sequential
    
    Graph->>BookingAgent: Execute first
    BookingAgent-->>Graph: Booking #12345 info (150ms)
    
    Graph->>Graph: Pass booking context
    
    Graph->>ComplaintAgent: Execute with context
    ComplaintAgent-->>Graph: Complaint #C789 created (100ms)
    
    Graph->>Graph: Merge responses
    Graph->>Graph: Add provenance
    Graph-->>Coordinator: Combined response (250ms total)
    Coordinator-->>User: Formatted response
    
    Note over Graph,ComplaintAgent: Total time = 150ms + 100ms = 250ms
```

---

## 📊 DIAGRAM 6: Agent Routing

```mermaid
graph TD
    A[User Message] --> B[Intent Classification]
    
    B --> C{Primary Intent}
    
    C -->|service_inquiry| D1[ServiceAgent]
    C -->|service_discovery| D1
    C -->|service_browse| D1
    
    C -->|policy_inquiry| D2[PolicyAgent]
    C -->|policy_question| D2
    
    C -->|booking_create| D3[BookingAgent]
    C -->|booking_status| D3
    C -->|booking_modify| D3
    C -->|booking_reschedule| D3
    
    C -->|booking_cancel| D4[CancellationAgent]
    C -->|cancellation_inquiry| D4
    
    C -->|complaint| D5[ComplaintAgent]
    C -->|complaint_status| D5
    
    C -->|data_query| D6[SQLAgent]
    C -->|analytics| D6
    
    D1 --> E[Execute Agent]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    
    E --> F[Return Response]
    
    style C fill:#fff3cd
    style D1 fill:#d1ecf1
    style D2 fill:#d1ecf1
    style D3 fill:#d1ecf1
    style D4 fill:#d1ecf1
    style D5 fill:#d1ecf1
    style D6 fill:#d1ecf1
    style F fill:#d4edda
```

---

## 📊 DIAGRAM 7: Provenance Tracking

```mermaid
graph TD
    A[Multi-Agent Execution] --> B[Agent 1: ServiceAgent]
    A --> C[Agent 2: PolicyAgent]
    
    B --> D[Response 1]
    C --> E[Response 2]
    
    D --> F[Provenance Entry 1]
    E --> G[Provenance Entry 2]
    
    F --> H{Merge Responses}
    G --> H
    
    H --> I[Combined Response]
    
    I --> J[Provenance Array]
    
    J --> K["[
        {
            agent: 'service',
            contribution: 'AC service...',
            action_taken: 'service_retrieved',
            order: 1,
            execution_time_ms: 150,
            success: true
        },
        {
            agent: 'policy',
            contribution: 'Cancellation policy...',
            action_taken: 'policy_retrieved',
            order: 2,
            execution_time_ms: 200,
            success: true
        }
    ]"]
    
    K --> L[User Receives Response with Attribution]
    
    style A fill:#fff3cd
    style I fill:#d4edda
    style J fill:#e7f3ff
    style L fill:#d4edda
```

---

## 📊 DIAGRAM 8: Error Handling Flow

```mermaid
graph TD
    A[Execute Agents] --> B{Agent Execution}
    
    B -->|Success| C1[Agent 1: Success]
    B -->|Failure| C2[Agent 2: Exception]
    B -->|Timeout| C3[Agent 3: Timeout]
    
    C1 --> D[Collect Response]
    C2 --> E[Catch Exception]
    C3 --> F[Handle Timeout]
    
    E --> G[Create Error Response]
    F --> H[Create Timeout Response]
    
    D --> I[Merge All Responses]
    G --> I
    H --> I
    
    I --> J{Any Success?}
    
    J -->|Yes| K[Return Partial Results]
    J -->|No| L[Return Error Message]
    
    K --> M[Mark Failed Agents in Provenance]
    L --> N[Log Error]
    
    M --> O[User Receives Response]
    N --> O
    
    style C1 fill:#d4edda
    style C2 fill:#f8d7da
    style C3 fill:#fff3cd
    style K fill:#d4edda
    style L fill:#f8d7da
```

---

## 📊 DIAGRAM 9: Timeout Mechanism

```mermaid
sequenceDiagram
    participant Graph
    participant Agent1
    participant Agent2
    participant Agent3
    
    Graph->>Graph: Start timer (30s)
    
    par Parallel Execution
        Graph->>Agent1: Execute
        Agent1-->>Graph: Response (100ms)
    and
        Graph->>Agent2: Execute
        Agent2-->>Graph: Response (200ms)
    and
        Graph->>Agent3: Execute
        Note over Agent3: Takes too long (35s)
    end
    
    Graph->>Graph: Timeout reached (30s)
    Graph->>Graph: Cancel Agent3
    
    Graph->>Graph: Collect available responses
    Graph->>Graph: Mark Agent3 as timeout
    
    Graph-->>Graph: Return partial results
    
    Note over Graph: Total time = 30s (timeout)
    Note over Graph: Agent1 & Agent2 succeeded
    Note over Graph: Agent3 marked as timeout
```

---

## 📊 DIAGRAM 10: State Management

```mermaid
graph LR
    A[Initial State] --> B[Add Intent Result]
    B --> C[Add User Info]
    C --> D[Add Session ID]
    
    D --> E[Prepare Execution Node]
    E --> F[Add Execution Plan]
    F --> G[Add Independent Intents]
    G --> H[Add Dependent Intents]
    
    H --> I[Parallel Execution Node]
    I --> J[Add Parallel Responses]
    
    J --> K[Sequential Execution Node]
    K --> L[Add Sequential Responses]
    
    L --> M[Merge Responses Node]
    M --> N[Add Final Response]
    N --> O[Add Provenance]
    O --> P[Add Combined Metadata]
    
    P --> Q[Final State]
    
    style A fill:#e1f5ff
    style Q fill:#d4edda
    style F fill:#fff3cd
    style J fill:#d1ecf1
    style L fill:#f8d7da
    style O fill:#e7f3ff
```

---

## 🎯 KEY INSIGHTS FROM DIAGRAMS

### **1. Parallel Execution Benefits**
- Independent intents execute concurrently
- Total time = max(agent_times), not sum
- Significant performance improvement (1.5-2x faster)

### **2. Dependency Management**
- Automatic detection of intent dependencies
- Sequential execution when needed
- Context passing between dependent agents

### **3. Error Resilience**
- Individual agent failures don't crash system
- Partial results returned when possible
- Comprehensive error tracking in provenance

### **4. Provenance Tracking**
- Every agent contribution tracked
- Execution order recorded
- Performance metrics included
- Success/failure status tracked

### **5. State Management**
- Immutable state updates
- Context-aware execution
- Complete audit trail

---

## 📝 USAGE EXAMPLES

### **Example 1: Independent Intents (Parallel)**
```
User: "Tell me about AC service AND show cancellation policy"

Flow:
1. Intent Classification → 2 intents detected
2. Dependency Analysis → Both independent
3. Parallel Execution → ServiceAgent & PolicyAgent run concurrently
4. Response Merging → Combined response with provenance
5. User receives formatted response

Time: ~200ms (max of both agents)
```

### **Example 2: Dependent Intents (Sequential)**
```
User: "Show my booking AND file a complaint"

Flow:
1. Intent Classification → 2 intents detected
2. Dependency Analysis → complaint depends on booking_status
3. Sequential Execution → BookingAgent first, then ComplaintAgent
4. Context Passing → Booking info passed to ComplaintAgent
5. Response Merging → Combined response with provenance
6. User receives formatted response

Time: ~250ms (sum of both agents)
```

---

## 🔧 TECHNICAL NOTES

### **Parallel Execution**
- Uses `asyncio.gather()` for true concurrency
- Timeout protection (30 seconds default)
- Exception handling with `return_exceptions=True`

### **Sequential Execution**
- Context passed between agents
- Each agent can use previous results
- Maintains execution order

### **Response Merging**
- Intelligent formatting based on agent count
- Provenance tracking for attribution
- Metadata aggregation

### **Error Handling**
- Node-level try/catch
- Agent-level exception handling
- Timeout-level protection
- Fallback to sequential execution

---

**End of Workflow Diagrams**

