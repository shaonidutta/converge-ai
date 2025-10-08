# Next Steps - Phase 8: Vector DB Service Layer & Search APIs

**Project**: ConvergeAI  
**Date**: 2025-10-08  
**Current Status**: Phase 7 Complete ✅ → Phase 8 Ready to Start

---

## ✅ PHASE 7 COMPLETED

### What Was Accomplished:
1. ✅ Finalized scalable vector DB structure (subcategory-level, not rate card-level)
2. ✅ Created Pinecone serverless index: `convergeai` (AWS us-east-1, 384 dims)
3. ✅ Converted Terms & Conditions to PDF
4. ✅ Generated 76 subcategory-level service descriptions (Markdown + PDF)
5. ✅ Generated embeddings using sentence-transformers/all-MiniLM-L6-v2
6. ✅ Ingested 239 vectors to Pinecone:
   - 22 vectors in `documents` namespace (3 policy PDFs)
   - 217 vectors in `service-descriptions` namespace (76 subcategories)
7. ✅ Documented complete architecture and integration patterns

### Vector DB Status:
- **Index**: `convergeai` (Pinecone Serverless)
- **Namespaces**: `documents`, `service-descriptions` (reviews namespace ready)
- **Total Vectors**: 239
- **Monthly Cost**: $0.60-$1.50 (scalable to millions of rate cards)
- **Scalability**: Can handle millions of rate cards with same vector count!

---

## 🚀 PHASE 8: VECTOR DB SERVICE LAYER & SEARCH APIs

### Overview:
Build the service layer and REST APIs to enable semantic search and integrate Vector DB with MySQL for real-time pricing.

---

## 📋 TASK BREAKDOWN

### **Task 1: Create Vector DB Service Layer** ⏭️ START HERE

#### 1.1 Create PineconeService Class
**File**: `backend/src/services/vector_db/pinecone_service.py`

**What to implement**:
```python
class PineconeService:
    """Service for Pinecone vector database operations"""
    
    def __init__(self):
        # Initialize Pinecone client
        # Load embedding model
        
    async def search(
        self, 
        query: str, 
        namespace: str, 
        top_k: int = 5,
        filter: Dict = None
    ) -> List[Dict]:
        """Semantic search in specified namespace"""
        # 1. Generate embedding for query
        # 2. Search Pinecone
        # 3. Return results with metadata
        
    async def search_services(
        self,
        query: str,
        category_id: int = None,
        max_results: int = 5
    ) -> List[Dict]:
        """Search services in service-descriptions namespace"""
        # 1. Build filter if category_id provided
        # 2. Search Vector DB
        # 3. Extract subcategory_ids from results
        # 4. Return service matches
        
    async def search_policies(
        self,
        query: str,
        document_type: str = None
    ) -> List[Dict]:
        """Search policy documents in documents namespace"""
        # 1. Build filter if document_type provided
        # 2. Search Vector DB
        # 3. Return policy matches
```

**Dependencies**:
- `pinecone` library
- `sentence-transformers` library
- Settings from `src/core/config/settings.py`

---

#### 1.2 Create ServiceSearchService Class
**File**: `backend/src/services/search/service_search.py`

**What to implement**:
```python
class ServiceSearchService:
    """Service for searching services with MySQL integration"""
    
    def __init__(self, db: Session, pinecone_service: PineconeService):
        self.db = db
        self.pinecone = pinecone_service
        
    async def search_services_with_pricing(
        self,
        query: str,
        pincode: str = None,
        category_id: int = None,
        max_price: float = None
    ) -> Dict:
        """
        Search services and fetch pricing from MySQL
        
        Flow:
        1. Search Vector DB → Get subcategory_ids
        2. Query MySQL → Get all rate cards for those subcategories
        3. Filter by pincode if provided
        4. Filter by max_price if provided
        5. Combine and return
        """
        # 1. Vector DB search
        vector_results = await self.pinecone.search_services(query, category_id)
        
        # 2. Extract subcategory_ids
        subcategory_ids = [r['metadata']['subcategory_id'] for r in vector_results]
        
        # 3. MySQL query
        rate_cards = self.db.query(RateCard).filter(
            RateCard.subcategory_id.in_(subcategory_ids),
            RateCard.is_active == True
        ).all()
        
        # 4. Filter by pincode
        if pincode:
            rate_cards = [rc for rc in rate_cards if pincode in rc.pincodes]
        
        # 5. Filter by price
        if max_price:
            rate_cards = [rc for rc in rate_cards if rc.price <= max_price]
        
        # 6. Group by subcategory and combine
        return self._combine_results(vector_results, rate_cards)
```

---

### **Task 2: Create Search API Endpoints**

#### 2.1 Create Search Router
**File**: `backend/src/api/v1/routes/search.py`

**Endpoints to implement**:

```python
@router.post("/services", response_model=ServiceSearchResponse)
async def search_services(
    request: ServiceSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search services with semantic search + MySQL pricing
    
    Request Body:
    {
        "query": "AC repair for split AC",
        "pincode": "110001",  # optional
        "category_id": 2,     # optional
        "max_price": 5000     # optional
    }
    
    Response:
    {
        "query": "AC repair for split AC",
        "results": [
            {
                "subcategory_id": 9,
                "subcategory_name": "AC Repair",
                "category_name": "Appliance Repair",
                "description": "Expert AC repair service...",
                "variants": [
                    {
                        "id": 102,
                        "name": "AC Repair - Standard",
                        "price": 3532.64,
                        "strike_price": 4500.00,
                        "discount_percentage": 21,
                        "available": true
                    }
                ]
            }
        ]
    }
    """
    service_search = ServiceSearchService(db, pinecone_service)
    results = await service_search.search_services_with_pricing(
        query=request.query,
        pincode=request.pincode,
        category_id=request.category_id,
        max_price=request.max_price
    )
    return results


@router.post("/policies", response_model=PolicySearchResponse)
async def search_policies(
    request: PolicySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search policy documents
    
    Request Body:
    {
        "query": "Can I cancel my booking?",
        "document_type": "terms"  # optional: terms, privacy, refund
    }
    
    Response:
    {
        "query": "Can I cancel my booking?",
        "results": [
            {
                "document_type": "terms",
                "title": "Terms and Conditions",
                "section": "5. BOOKINGS - Cancellation",
                "content": "You may cancel your booking...",
                "relevance_score": 0.92
            }
        ]
    }
    """
    results = await pinecone_service.search_policies(
        query=request.query,
        document_type=request.document_type
    )
    return {"query": request.query, "results": results}
```

---

#### 2.2 Create Request/Response Schemas
**File**: `backend/src/api/v1/schemas/search.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ServiceSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    pincode: Optional[str] = Field(None, description="Filter by pincode")
    category_id: Optional[int] = Field(None, description="Filter by category")
    max_price: Optional[float] = Field(None, description="Maximum price filter")

class ServiceVariant(BaseModel):
    id: int
    name: str
    price: float
    strike_price: Optional[float]
    discount_percentage: Optional[int]
    available: bool

class ServiceResult(BaseModel):
    subcategory_id: int
    subcategory_name: str
    category_name: str
    description: str
    relevance_score: float
    variants: List[ServiceVariant]

class ServiceSearchResponse(BaseModel):
    query: str
    results: List[ServiceResult]
    total_results: int

class PolicySearchRequest(BaseModel):
    query: str
    document_type: Optional[str] = Field(None, description="Filter by document type")

class PolicyResult(BaseModel):
    document_type: str
    title: str
    section: Optional[str]
    content: str
    relevance_score: float

class PolicySearchResponse(BaseModel):
    query: str
    results: List[PolicyResult]
```

---

### **Task 3: Add Redis Caching**

#### 3.1 Create Cache Service
**File**: `backend/src/services/cache/search_cache.py`

```python
class SearchCacheService:
    """Cache service for search results"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour
        
    async def get_cached_search(self, query: str, filters: Dict) -> Optional[Dict]:
        """Get cached search results"""
        cache_key = self._generate_cache_key(query, filters)
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
        
    async def cache_search_results(self, query: str, filters: Dict, results: Dict):
        """Cache search results"""
        cache_key = self._generate_cache_key(query, filters)
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(results)
        )
```

---

### **Task 4: Testing**

#### 4.1 Unit Tests
**File**: `backend/tests/services/test_pinecone_service.py`

Test cases:
- Test search method
- Test filter functionality
- Test error handling
- Test embedding generation

#### 4.2 Integration Tests
**File**: `backend/tests/api/test_search_endpoints.py`

Test cases:
- Test service search API
- Test policy search API
- Test with various filters
- Test pagination
- Test error responses

---

### **Task 5: Documentation**

#### 5.1 API Documentation
- Add OpenAPI/Swagger documentation
- Add request/response examples
- Document filter options
- Add error codes

#### 5.2 Developer Guide
- Document Vector DB integration pattern
- Add code examples
- Document caching strategy
- Add troubleshooting guide

---

## 📊 ESTIMATED TIMELINE

| Task | Estimated Time | Priority |
|------|----------------|----------|
| PineconeService Class | 2-3 hours | HIGH |
| ServiceSearchService Class | 2-3 hours | HIGH |
| Search API Endpoints | 2-3 hours | HIGH |
| Request/Response Schemas | 1 hour | HIGH |
| Redis Caching | 1-2 hours | MEDIUM |
| Unit Tests | 2-3 hours | HIGH |
| Integration Tests | 2-3 hours | HIGH |
| Documentation | 1-2 hours | MEDIUM |
| **TOTAL** | **13-20 hours** | - |

---

## 🎯 SUCCESS CRITERIA

- [ ] PineconeService class implemented and tested
- [ ] ServiceSearchService class implemented with MySQL integration
- [ ] Search APIs working end-to-end
- [ ] Vector DB + MySQL combined queries working
- [ ] Redis caching implemented
- [ ] All tests passing
- [ ] API documentation complete
- [ ] Performance: Search latency < 200ms

---

## 📁 FILES TO CREATE

1. `backend/src/services/vector_db/__init__.py`
2. `backend/src/services/vector_db/pinecone_service.py`
3. `backend/src/services/search/__init__.py`
4. `backend/src/services/search/service_search.py`
5. `backend/src/services/cache/search_cache.py`
6. `backend/src/api/v1/routes/search.py`
7. `backend/src/api/v1/schemas/search.py`
8. `backend/tests/services/test_pinecone_service.py`
9. `backend/tests/api/test_search_endpoints.py`

---

## 🚀 AFTER PHASE 8

### Phase 9: Multi-Agent System (LangGraph)
- Design agent architecture
- Implement coordinator agent
- Implement specialized agents (Service, Policy, Booking)
- Integrate with vector DB search

### Phase 10: Review Sync
- Real-time review ingestion to Pinecone
- Review agent implementation

### Phase 11: Frontend Development
- Customer mobile app
- Service provider app
- Operations dashboard

---

**Status**: ✅ Ready to start Phase 8!  
**Next Action**: Create `backend/src/services/vector_db/pinecone_service.py`

