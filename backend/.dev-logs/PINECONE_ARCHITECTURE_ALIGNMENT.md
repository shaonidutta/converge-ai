# Pinecone Architecture Alignment

**Date**: 2025-10-07  
**Purpose**: Align Pinecone implementation with original brainstorming architecture

---

## Original Architecture (From Brainstorming)

**Source**: `brainstorming/architecture_complete.md` - Section 3: Vector Database Schema

### Original 4 Collections Design

From the original brainstorming, we defined **4 core collections**:

#### 1. Documents Collection
```python
{
    "id": "doc_policy_cancellation_001",
    "vector": [0.123, 0.456, ...],  # 768-dim embedding (now 384-dim)
    "metadata": {
        "doc_type": "policy",
        "category": "cancellation",
        "title": "Cancellation Policy",
        "chunk_id": 1,
        "total_chunks": 5,
        "source_file": "policies/cancellation.pdf",
        "last_updated": "2025-01-15"
    },
    "text": "Customers can cancel bookings up to 4 hours before..."
}
```

**Purpose**: Policy documents, T&C, FAQs

#### 2. Service Descriptions Collection
```python
{
    "id": "service_desc_42_chunk_1",
    "vector": [0.234, 0.567, ...],
    "metadata": {
        "service_id": 42,
        "category_id": 5,
        "subcategory_id": 23,
        "service_name": "AC Deep Cleaning",
        "chunk_id": 1
    },
    "text": "Our AC deep cleaning service includes complete dismantling..."
}
```

**Purpose**: Service catalog descriptions

#### 3. Reviews Collection
```python
{
    "id": "review_12345",
    "vector": [0.345, 0.678, ...],
    "metadata": {
        "provider_id": 201,
        "service_id": 42,
        "rating": 4.5,
        "booking_id": 9876,
        "created_at": 1704067200
    },
    "text": "Excellent service! The technician was professional and thorough..."
}
```

**Purpose**: Customer reviews and feedback

#### 4. Chat History Collection
```python
{
    "id": "chat_session_s123_msg_5",
    "vector": [0.456, 0.789, ...],
    "metadata": {
        "session_id": "s123",
        "user_id": 456,
        "intent": "booking_intent",
        "resolved": true,
        "created_at": 1704067200
    },
    "text": "I want to book AC servicing for tomorrow at 10 AM"
}
```

**Purpose**: Chat sessions for similarity search

---

## Updated Implementation

### Pinecone Serverless Structure

**Index**: `convergeai-documents`  
**Dimension**: 384 (sentence-transformers/all-MiniLM-L6-v2)  
**Metric**: Cosine similarity  
**Region**: us-east-1 (AWS)

### 4 Namespaces (Collections)

```
convergeai-documents (Index)
├── documents/                   # Policy docs, T&C, FAQs, guides
├── service-descriptions/        # Service catalog & descriptions
├── reviews/                     # Customer reviews & feedback
└── chat-history/                # Chat sessions for similarity search
```

### Alignment with Original Design

| Original Collection | Implementation Namespace | Status | Notes |
|---------------------|-------------------------|--------|-------|
| Documents Collection | `documents` | ✅ Aligned | Added sub-categories via metadata |
| Service Descriptions | `service-descriptions` | ✅ Aligned | Enhanced with pricing, features |
| Reviews Collection | `reviews` | ✅ Aligned | Added sentiment, verification |
| Chat History | `chat-history` | ✅ Aligned | Added intent, resolution tracking |

---

## Key Enhancements

### 1. Documents Collection Enhancements

**Original**: Basic policy documents  
**Enhanced**: 
- Sub-categorization via `doc_type` (policy, faq, guide, training, knowledge)
- Version control via `version` and `is_current`
- Compliance tracking via `compliance` array
- User feedback via `view_count` and `helpful_votes`
- Related documents linking

### 2. Service Descriptions Enhancements

**Original**: Basic service info  
**Enhanced**:
- Pincode-based filtering
- Price range metadata
- Duration and features
- Popularity scoring
- Active/inactive status

### 3. Reviews Collection Enhancements

**Original**: Basic review text  
**Enhanced**:
- Sentiment analysis
- Verified booking flag
- Helpful count tracking
- Provider response tracking
- Service date tracking

### 4. Chat History Enhancements

**Original**: Basic conversation text  
**Enhanced**:
- Intent and entity extraction
- Resolution tracking
- Agent attribution
- Satisfaction scoring
- Conversation length metrics

---

## Metadata Schema Comparison

### Documents Collection

| Field | Original | Enhanced | Purpose |
|-------|----------|----------|---------|
| doc_type | ✅ | ✅ | Document categorization |
| category | ✅ | ✅ | Sub-category |
| title | ✅ | ✅ | Document title |
| chunk_id | ✅ | ✅ | Chunk identification |
| source_file | ✅ | ✅ | Source reference |
| last_updated | ✅ | ✅ | Version tracking |
| applicability | ❌ | ✅ | User type filtering |
| compliance | ❌ | ✅ | Legal compliance |
| version | ❌ | ✅ | Version control |
| helpful_votes | ❌ | ✅ | User feedback |

### Service Descriptions Collection

| Field | Original | Enhanced | Purpose |
|-------|----------|----------|---------|
| service_id | ✅ | ✅ | MySQL reference |
| category_id | ✅ | ✅ | Category reference |
| subcategory_id | ✅ | ✅ | Subcategory reference |
| service_name | ✅ | ✅ | Service name |
| chunk_id | ✅ | ✅ | Chunk identification |
| pincodes | ❌ | ✅ | Location filtering |
| price_range | ❌ | ✅ | Price filtering |
| duration_minutes | ❌ | ✅ | Duration info |
| popularity_score | ❌ | ✅ | Ranking |
| features | ❌ | ✅ | Feature list |

### Reviews Collection

| Field | Original | Enhanced | Purpose |
|-------|----------|----------|---------|
| provider_id | ✅ | ✅ | Provider reference |
| service_id | ✅ | ✅ | Service reference |
| rating | ✅ | ✅ | Star rating |
| booking_id | ✅ | ✅ | Booking reference |
| created_at | ✅ | ✅ | Timestamp |
| sentiment | ❌ | ✅ | Sentiment analysis |
| verified_booking | ❌ | ✅ | Verification flag |
| helpful_count | ❌ | ✅ | User feedback |
| service_date | ❌ | ✅ | Service date |

### Chat History Collection

| Field | Original | Enhanced | Purpose |
|-------|----------|----------|---------|
| session_id | ✅ | ✅ | Session reference |
| user_id | ✅ | ✅ | User reference |
| intent | ✅ | ✅ | Intent classification |
| resolved | ✅ | ✅ | Resolution status |
| created_at | ✅ | ✅ | Timestamp |
| entities | ❌ | ✅ | Entity extraction |
| resolution_type | ❌ | ✅ | How resolved |
| agent_used | ❌ | ✅ | Agent attribution |
| satisfaction_score | ❌ | ✅ | User satisfaction |

---

## Agent Usage Patterns

### Policy Agent
- **Collection**: `documents`
- **Filters**: `doc_type=policy`, `applicability`, `is_current`
- **Use Case**: Answer policy questions with citations

### Service Agent
- **Collection**: `service-descriptions`
- **Filters**: `category_id`, `pincode`, `is_active`
- **Use Case**: Service discovery and information

### Booking Agent
- **Collections**: `service-descriptions` + `reviews`
- **Filters**: Service filters + rating filters
- **Use Case**: Service recommendation with reviews

### Complaint Agent
- **Collections**: `documents` + `chat-history`
- **Filters**: `doc_type=guide`, `intent=complaint`
- **Use Case**: Resolution guidance from past cases

### Coordinator Agent
- **Collection**: `chat-history`
- **Filters**: `intent`, `resolved`, `satisfaction_score`
- **Use Case**: Learn from similar conversations

---

## Implementation Status

### Completed ✅
1. ✅ Pinecone service implementation
2. ✅ Embedding service (384-dim)
3. ✅ Metadata schema design
4. ✅ Architecture alignment
5. ✅ Policy documents created

### In Progress ⏭️
1. ⏭️ Create 4 namespaces in Pinecone
2. ⏭️ Document ingestion pipeline
3. ⏭️ Service descriptions extraction
4. ⏭️ Reviews ingestion
5. ⏭️ Chat history ingestion

### Pending 📋
1. 📋 Metadata validation schemas
2. 📋 Search optimization
3. 📋 Performance testing
4. 📋 Agent integration

---

## Cost Estimation

### Storage Costs (Pinecone Serverless)

| Namespace | Vectors | Size per Vector | Total Size | Monthly Cost |
|-----------|---------|-----------------|------------|--------------|
| documents | 2,000 | 1.5 KB | 3 MB | $0.008 |
| service-descriptions | 1,000 | 1.5 KB | 1.5 MB | $0.004 |
| reviews | 10,000 | 1.5 KB | 15 MB | $0.040 |
| chat-history | 50,000 | 1.5 KB | 75 MB | $0.200 |
| **Total** | **63,000** | - | **94.5 MB** | **$0.252** |

### Query Costs (1M queries/month)
- Read units: ~$0.20/month
- **Total Monthly Cost**: ~**$0.45/month**

**Note**: Extremely cost-effective for serverless deployment!

---

## Next Steps

1. **Immediate**: Create namespaces in Pinecone
2. **Week 1**: Ingest policy documents
3. **Week 2**: Extract and ingest service descriptions
4. **Week 3**: Ingest reviews (from MySQL)
5. **Week 4**: Set up chat history ingestion pipeline

---

## Conclusion

✅ **Fully aligned** with original brainstorming architecture  
✅ **Enhanced** with additional metadata for better filtering  
✅ **Cost-effective** serverless implementation  
✅ **Production-ready** schema design  
✅ **Scalable** to millions of vectors  

**Ready for**: Namespace creation and document ingestion

---

*Document Version: 1.0*  
*Date: 2025-10-07*  
*Author: AI Assistant*

