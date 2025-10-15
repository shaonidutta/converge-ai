# PolicyAgent (RAG) - Implementation Plan

**Date**: 2025-10-14  
**Branch**: `feature/policy-agent-rag`  
**Priority**: HIGH (Customer Support Critical)

---

## 🎯 **OBJECTIVE**

Implement **PolicyAgent** - an AI agent that uses **Retrieval-Augmented Generation (RAG)** to answer customer questions about policies, terms, conditions, refunds, cancellations, and other company policies by retrieving relevant information from a vector database (Pinecone) and generating accurate, grounded responses.

---

## 📋 **REQUIREMENTS**

### **Core Functionality**
1. ✅ Vector search for policy documents in Pinecone
2. ✅ Context retrieval with relevance scoring
3. ✅ Response generation with LLM (Gemini 2.0 Flash)
4. ✅ Citation and source attribution
5. ✅ Grounding score calculation (prevent hallucinations)
6. ✅ Multi-document policy queries
7. ✅ Fallback for no relevant documents found

### **Technical Requirements**
- **Vector Database**: Pinecone (already configured)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM**: Gemini 2.0 Flash (gemini-2.0-flash)
- **Framework**: LangChain for RAG pipeline
- **Index**: Pinecone Serverless (us-east-1)

---

## 🏗️ **ARCHITECTURE**

### **RAG Pipeline Flow**
```
User Query
    ↓
1. Query Embedding (sentence-transformers)
    ↓
2. Vector Search in Pinecone (top_k=5)
    ↓
3. Context Retrieval (relevant policy chunks)
    ↓
4. Prompt Construction (query + context)
    ↓
5. LLM Generation (Gemini 2.0 Flash)
    ↓
6. Citation Addition (source references)
    ↓
7. Grounding Score Calculation
    ↓
Response with Sources
```

### **PolicyAgent Methods**

```python
class PolicyAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pinecone_service = PineconeService()
        self.embedding_service = EmbeddingService()
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, intent: str, entities: Dict[str, Any], user: User, session_id: str) -> Dict[str, Any]:
        """Main execution method - routes to appropriate handler"""
        
    async def _search_policies(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant policy documents in Pinecone"""
        
    async def _retrieve_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Extract and format context from search results"""
        
    async def _generate_response(self, query: str, context: str) -> str:
        """Generate response using LLM with retrieved context"""
        
    async def _add_citations(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add source citations to response"""
        
    async def _calculate_grounding_score(self, response: str, context: str) -> float:
        """Calculate how well the response is grounded in the context"""
```

---

## 📊 **DATA REQUIREMENTS**

### **Policy Documents to Index**
1. **Cancellation Policy**
   - Refund eligibility criteria
   - Cancellation timeframes
   - Refund processing time
   - Partial refund rules

2. **Booking Policy**
   - Booking confirmation process
   - Payment terms
   - Rescheduling rules
   - Service guarantee

3. **Privacy Policy**
   - Data collection
   - Data usage
   - Data sharing
   - User rights

4. **Terms of Service**
   - User responsibilities
   - Service limitations
   - Liability clauses
   - Dispute resolution

5. **Refund Policy**
   - Refund eligibility
   - Refund methods
   - Processing timeframes
   - Exceptions

### **Document Chunking Strategy**
- **Chunk Size**: 500 tokens
- **Overlap**: 50 tokens
- **Metadata**: 
  - `policy_type`: cancellation, booking, privacy, terms, refund
  - `section`: section name
  - `last_updated`: date
  - `version`: policy version

---

## 🔧 **IMPLEMENTATION STEPS**

### **Phase 1: Setup and Configuration** (Day 1)
1. ✅ Create `backend/src/agents/policy/` directory
2. ✅ Create `policy_agent.py` file
3. ✅ Verify Pinecone connection and index
4. ✅ Verify embedding service works
5. ✅ Test vector search functionality

### **Phase 2: Core Implementation** (Day 2)
1. ✅ Implement `execute()` method with routing
2. ✅ Implement `_search_policies()` with Pinecone
3. ✅ Implement `_retrieve_context()` with formatting
4. ✅ Implement `_generate_response()` with LLM
5. ✅ Implement `_add_citations()` with source tracking
6. ✅ Implement `_calculate_grounding_score()` with validation

### **Phase 3: Policy Document Preparation** (Day 2-3)
1. ✅ Create policy documents in markdown format
2. ✅ Chunk documents with overlap
3. ✅ Generate embeddings for all chunks
4. ✅ Upload to Pinecone with metadata
5. ✅ Verify search returns relevant results

### **Phase 4: Testing** (Day 3)
1. ✅ Create unit tests for each method
2. ✅ Create integration tests with real Pinecone
3. ✅ Test with various policy queries
4. ✅ Verify citations are accurate
5. ✅ Verify grounding scores are reasonable

### **Phase 5: Documentation and Deployment** (Day 4)
1. ✅ Document all methods with docstrings
2. ✅ Create usage examples
3. ✅ Update AI_AGENTS_STATUS.md
4. ✅ Commit and push to feature branch
5. ✅ Create Pull Request

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
# backend/tests/test_policy_agent.py

async def test_policy_agent_search_policies():
    """Test policy search returns relevant results"""
    
async def test_policy_agent_retrieve_context():
    """Test context extraction and formatting"""
    
async def test_policy_agent_generate_response():
    """Test LLM response generation"""
    
async def test_policy_agent_add_citations():
    """Test citation addition"""
    
async def test_policy_agent_calculate_grounding_score():
    """Test grounding score calculation"""
```

### **Integration Tests**
```python
# backend/tests/integration/test_policy_agent_integration.py

async def test_policy_agent_cancellation_query():
    """Test cancellation policy query end-to-end"""
    
async def test_policy_agent_refund_query():
    """Test refund policy query end-to-end"""
    
async def test_policy_agent_no_relevant_docs():
    """Test fallback when no relevant documents found"""
    
async def test_policy_agent_multi_document_query():
    """Test query spanning multiple policy documents"""
```

---

## 📝 **EXAMPLE USAGE**

### **Input**
```python
{
    "intent": "policy_inquiry",
    "entities": {
        "query": "What is your cancellation policy? Can I get a refund if I cancel 2 hours before?"
    },
    "user": user_object,
    "session_id": "session_123"
}
```

### **Output**
```python
{
    "response": "According to our cancellation policy, you can cancel your booking and receive a full refund if you cancel at least 4 hours before the scheduled service time. If you cancel between 2-4 hours before, you'll receive a 50% refund. Cancellations made less than 2 hours before the service time are not eligible for a refund.",
    "action_taken": "policy_answered",
    "metadata": {
        "sources": [
            {
                "policy_type": "cancellation",
                "section": "Refund Eligibility",
                "relevance_score": 0.92
            },
            {
                "policy_type": "refund",
                "section": "Timeframes",
                "relevance_score": 0.87
            }
        ],
        "grounding_score": 0.95,
        "confidence": "high"
    }
}
```

---

## 🚨 **CRITICAL CONSIDERATIONS**

### **Hallucination Prevention**
1. ✅ Always include source citations
2. ✅ Calculate grounding score (>0.7 = good)
3. ✅ If grounding score < 0.5, return "I don't have enough information"
4. ✅ Never generate information not in retrieved context

### **Security**
1. ✅ No user data in policy documents
2. ✅ No sensitive company information
3. ✅ Rate limiting on queries
4. ✅ Input validation and sanitization

### **Performance**
1. ✅ Cache frequently asked questions
2. ✅ Optimize vector search (top_k=5 max)
3. ✅ Timeout for LLM generation (10 seconds)
4. ✅ Async operations throughout

---

## 📊 **SUCCESS METRICS**

1. ✅ Retrieval accuracy > 90% (relevant docs in top 5)
2. ✅ Grounding score > 0.7 for all responses
3. ✅ Response time < 3 seconds
4. ✅ Citation accuracy 100%
5. ✅ Zero hallucinations in testing

---

## 🎯 **DELIVERABLES**

1. ✅ `backend/src/agents/policy/policy_agent.py` (500+ lines)
2. ✅ `backend/tests/test_policy_agent.py` (unit tests)
3. ✅ `backend/tests/integration/test_policy_agent_integration.py` (integration tests)
4. ✅ Policy documents in `backend/data/policies/` (markdown)
5. ✅ Pinecone index populated with policy embeddings
6. ✅ Documentation and examples

---

## 🚀 **NEXT STEPS AFTER COMPLETION**

1. Integrate PolicyAgent with ChatService
2. Add to CoordinatorAgent routing
3. Monitor grounding scores in production
4. Collect user feedback on policy answers
5. Continuously update policy documents

---

**Estimated Time**: 3-4 days  
**Status**: ⏳ **READY TO START**  
**Branch**: `feature/policy-agent-rag`

