# Pinecone Collections & Metadata Planning

**Project**: ConvergeAI/Nexora  
**Date**: 2025-10-07  
**Purpose**: Comprehensive planning for Pinecone namespaces (collections) and metadata schema

---

## Table of Contents

1. [Business Use Cases Analysis](#business-use-cases)
2. [Collection Strategy](#collection-strategy)
3. [Metadata Schema Design](#metadata-schema)
4. [Search & Filtering Requirements](#search-filtering)
5. [Implementation Plan](#implementation-plan)

---

## 1. Business Use Cases Analysis {#business-use-cases}

### 1.1 Customer-Facing Use Cases

#### A. Service Discovery & Booking
**Scenario**: Customer asks "I need AC servicing" or "What cleaning services do you offer?"
- **Need**: Search across service catalog (categories, subcategories, rate cards)
- **Data**: Service descriptions, features, pricing info, FAQs
- **Filters**: Category, location (pincode), price range, service type

#### B. Policy & Terms Queries
**Scenario**: "What is your refund policy?" or "How do cancellations work?"
- **Need**: Search across legal/policy documents
- **Data**: Terms & Conditions, Privacy Policy, Refund Policy, Cancellation Policy
- **Filters**: Document type, section, applicability (customer/provider)

#### C. Complaint Resolution
**Scenario**: "My service was delayed" or "Provider didn't show up"
- **Need**: Search similar complaints, resolutions, escalation procedures
- **Data**: Complaint resolution templates, SLA guidelines, escalation paths
- **Filters**: Complaint type, priority, resolution status

#### D. General FAQs
**Scenario**: "How do I track my booking?" or "What payment methods do you accept?"
- **Need**: Search across general help content
- **Data**: FAQs, how-to guides, troubleshooting steps
- **Filters**: Topic, user type (customer/provider)

### 1.2 Provider-Facing Use Cases

#### A. Service Guidelines
**Scenario**: Provider needs to know service standards
- **Need**: Search service execution guidelines
- **Data**: Service checklists, quality standards, safety protocols
- **Filters**: Service category, certification level

#### B. Earnings & Payments
**Scenario**: "How do I get paid?" or "What are the commission rates?"
- **Need**: Search payment policies, commission structure
- **Data**: Payment terms, commission rates, payout schedules
- **Filters**: Service type, provider tier

### 1.3 Operations Team Use Cases

#### A. Training Materials
**Scenario**: New ops staff needs training
- **Need**: Search training docs, SOPs, best practices
- **Data**: Training manuals, process documents, case studies
- **Filters**: Department, role, topic

#### B. Escalation Procedures
**Scenario**: Handle critical complaints
- **Need**: Search escalation guidelines, contact info
- **Data**: Escalation matrix, contact lists, SLA definitions
- **Filters**: Priority level, department

### 1.4 AI Agent Use Cases

#### A. Booking Agent
- **Need**: Service details, availability rules, pricing logic
- **Data**: Service catalog, rate card details, booking rules
- **Filters**: Category, pincode, date range

#### B. Cancellation Agent
- **Need**: Cancellation policies, refund calculation rules
- **Data**: Cancellation policy, refund matrix, timeline rules
- **Filters**: Booking status, time before service, payment method

#### C. Complaint Agent
- **Need**: Resolution templates, escalation criteria
- **Data**: Complaint handling guides, resolution scripts
- **Filters**: Complaint type, severity, SLA status

#### D. Policy Agent
- **Need**: All policy documents, terms, legal content
- **Data**: Complete policy library
- **Filters**: Document type, section, last updated

---

## 2. Collection Strategy {#collection-strategy}

### 2.1 Namespace Design

**Pinecone Serverless** uses **namespaces** to logically separate vectors within a single index.

#### Original Architecture (From Brainstorming)

Based on `brainstorming/architecture_complete.md`, we defined **4 core collections**:

1. **Documents Collection** - Policy documents, T&C, FAQs
2. **Service Descriptions Collection** - Service catalog descriptions
3. **Reviews Collection** - Customer reviews
4. **Chat History Collection** - For similarity search

#### Revised Namespace Structure (Aligned with Original Plan)

```
convergeai-documents (Index)
├── documents/                   # Policy docs, T&C, FAQs, guides
├── service-descriptions/        # Service catalog & descriptions
├── reviews/                     # Customer reviews & feedback
└── chat-history/                # Chat sessions for similarity search
```

**Note**: We'll use **sub-categorization via metadata** instead of separate namespaces for better flexibility.

### 2.2 Namespace Details

| Namespace | Purpose | Primary Users | Estimated Vectors |
|-----------|---------|---------------|-------------------|
| `documents` | Policies, T&C, FAQs, guides, training | Policy Agent, All Users | 1,000-2,000 |
| `service-descriptions` | Service catalog, features, pricing | Booking Agent, Service Agent | 500-1,000 |
| `reviews` | Customer reviews, ratings, feedback | All Agents, Customers | 5,000-10,000 |
| `chat-history` | Past conversations for similarity | Coordinator, All Agents | 10,000-50,000 |

**Total Estimated**: 16,500-63,000 vectors

**Rationale for 4 Collections**:
- ✅ **Simpler architecture** - Easier to manage and maintain
- ✅ **Clear separation** - Each collection has distinct purpose
- ✅ **Better performance** - Focused search within relevant collection
- ✅ **Aligned with original design** - Matches brainstorming architecture

### 2.3 Sub-Categorization via Metadata

Instead of creating many namespaces, we use **metadata filtering** for sub-categories:

**Documents Namespace** sub-categories (via `doc_type` metadata):
- `policy` - Terms, Privacy, Refund policies
- `faq` - Frequently asked questions
- `guide` - How-to guides, tutorials
- `training` - Internal training materials
- `knowledge` - General knowledge articles

**Service Descriptions Namespace** sub-categories (via `category_id` metadata):
- Organized by service categories (Home Cleaning, AC Repair, etc.)
- Further filtered by subcategory_id

**Reviews Namespace** sub-categories (via `service_id`, `provider_id` metadata):
- Organized by service and provider
- Filtered by rating, date, etc.

**Chat History Namespace** sub-categories (via `intent`, `resolved` metadata):
- Organized by intent type
- Filtered by resolution status

### 2.4 Why This Structure?

✅ **Aligned with Original Design**: Matches brainstorming architecture
✅ **Simpler Management**: 4 collections vs 8+ namespaces
✅ **Flexible Filtering**: Metadata provides fine-grained control
✅ **Better Performance**: Focused search within relevant collection
✅ **Scalable**: Easy to add new sub-categories via metadata
✅ **Cost-Effective**: Efficient use of Pinecone resources

---

## 3. Metadata Schema Design {#metadata-schema}

### 3.1 Common Metadata Fields (All Namespaces)

```python
{
    # Document Identification
    "document_id": "uuid",           # Unique document ID (MySQL reference)
    "chunk_id": "uuid",              # Unique chunk ID
    "chunk_index": 0,                # Position in document (0-based)
    
    # Content Info
    "document_name": "refund_policy.pdf",
    "document_type": "policy",       # policy, faq, service, guide, etc.
    "chunk_text": "Full text...",    # Original text (for display)
    "chunk_tokens": 245,             # Token count
    
    # Timestamps
    "created_at": "2025-10-07T10:30:00Z",
    "updated_at": "2025-10-07T10:30:00Z",
    "version": "1.0",                # Document version
    
    # Source Info
    "source_url": "https://...",     # Original source (if applicable)
    "uploaded_by": "user_id",        # Who uploaded/created
    
    # Search Optimization
    "language": "en",                # Language code
    "keywords": ["refund", "cancellation", "policy"],  # Extracted keywords
}
```

### 3.2 Collection-Specific Metadata

#### A. `documents` Collection (Namespace)

**Purpose**: Policy documents, T&C, FAQs, guides, training materials

```python
{
    # Common fields +
    "doc_type": "policy",            # policy, faq, guide, training, knowledge
    "category": "cancellation",      # Sub-category within doc_type
    "title": "Cancellation Policy",  # Document title
    "section": "refund_timeline",    # Section within document (if applicable)
    "applicability": "customer",     # customer, provider, both, ops
    "effective_date": "2025-01-01",  # When document became effective
    "jurisdiction": "India",         # Legal jurisdiction (for policies)
    "compliance": ["IT Act", "Consumer Protection Act"], # Compliance standards
    "is_current": true,              # Is this the current version?
    "version": "1.0",                # Document version
    "difficulty": "easy",            # easy, medium, hard (for FAQs/guides)
    "view_count": 1250,              # Popularity metric
    "helpful_votes": 980,            # User feedback
    "related_docs": ["doc_123", "doc_456"], # Related document IDs
}
```

**Sub-categories** (via `doc_type`):
- `policy` - Terms, Privacy, Refund, Cancellation policies
- `faq` - Frequently asked questions
- `guide` - How-to guides, tutorials
- `training` - Internal training materials
- `knowledge` - General knowledge articles

#### B. `service-descriptions` Collection (Namespace)

**Purpose**: Service catalog, features, pricing descriptions

```python
{
    # Common fields +
    "service_id": 42,                # MySQL service ID
    "category_id": 5,                # MySQL category ID
    "category_name": "AC Repair & Service",
    "subcategory_id": 23,            # MySQL subcategory ID
    "subcategory_name": "AC Deep Cleaning",
    "service_name": "AC Deep Cleaning",
    "service_type": "b2c",           # b2c, b2b, both
    "location_type": "pan_india",    # pan_india, specific
    "pincodes": ["110001", "110002"], # Applicable pincodes (if specific)
    "price_range": "500-2000",       # Price range
    "duration_minutes": 120,         # Service duration
    "is_active": true,               # Active status
    "popularity_score": 0.85,        # For ranking
    "features": ["dismantling", "cleaning", "reassembly"], # Key features
    "inclusions": ["gas check", "filter cleaning"], # What's included
}
```

#### C. `reviews` Collection (Namespace)

**Purpose**: Customer reviews and feedback

```python
{
    # Common fields +
    "review_id": 12345,              # MySQL review ID
    "provider_id": 201,              # MySQL provider ID
    "service_id": 42,                # MySQL service ID
    "booking_id": 9876,              # MySQL booking ID
    "user_id": 456,                  # MySQL user ID
    "rating": 4.5,                   # Star rating (1-5)
    "sentiment": "positive",         # positive, neutral, negative
    "verified_booking": true,        # Is this from verified booking?
    "helpful_count": 25,             # How many found it helpful
    "created_at": 1704067200,        # Unix timestamp
    "service_date": "2025-01-01",    # When service was provided
    "response_from_provider": false, # Did provider respond?
}
```

#### D. `chat-history` Collection (Namespace)

**Purpose**: Past conversations for similarity search and learning

```python
{
    # Common fields +
    "session_id": "s123",            # Chat session ID
    "message_id": 5,                 # Message number in session
    "user_id": 456,                  # MySQL user ID
    "user_type": "customer",         # customer, provider, ops
    "intent": "booking_intent",      # Detected intent
    "entities": {                    # Extracted entities
        "service": "AC cleaning",
        "date": "tomorrow",
        "time": "10 AM"
    },
    "resolved": true,                # Was query resolved?
    "resolution_type": "booking_created", # How it was resolved
    "agent_used": "booking_agent",   # Which agent handled it
    "satisfaction_score": 4.5,       # User satisfaction (if provided)
    "created_at": 1704067200,        # Unix timestamp
    "conversation_length": 8,        # Number of messages in conversation
}
```

---

## 3.3 Metadata Filtering Examples

### Example 1: Find refund policy for customers (documents namespace)
```python
namespace = "documents"
filter = {
    "doc_type": "policy",
    "category": "refund",
    "applicability": {"$in": ["customer", "both"]},
    "is_current": True
}
```

### Example 2: Find AC servicing descriptions in Delhi (service-descriptions namespace)
```python
namespace = "service-descriptions"
filter = {
    "category_name": "AC Repair & Service",
    "pincodes": {"$in": ["110001"]},
    "is_active": True
}
```

### Example 3: Find positive reviews for specific provider (reviews namespace)
```python
namespace = "reviews"
filter = {
    "provider_id": 201,
    "rating": {"$gte": 4.0},
    "sentiment": "positive",
    "verified_booking": True
}
```

### Example 4: Find similar resolved booking conversations (chat-history namespace)
```python
namespace = "chat-history"
filter = {
    "intent": "booking_intent",
    "resolved": True,
    "agent_used": "booking_agent",
    "satisfaction_score": {"$gte": 4.0}
}
```

### Example 5: Find FAQs about cancellation (documents namespace)
```python
namespace = "documents"
filter = {
    "doc_type": "faq",
    "category": "cancellation",
    "difficulty": {"$in": ["easy", "medium"]},
    "helpful_votes": {"$gte": 100}
}
```

---

## 4. Search & Filtering Requirements {#search-filtering}

### 4.1 Query Patterns

| Use Case | Namespace | Filters | Top K | Include Metadata |
|----------|-----------|---------|-------|------------------|
| Policy lookup | `documents` | doc_type=policy, category, applicability | 5 | Yes |
| FAQ search | `documents` | doc_type=faq, category, difficulty | 5 | Yes |
| Training search | `documents` | doc_type=training, role, difficulty | 10 | Yes |
| Service search | `service-descriptions` | category_id, pincode, is_active | 10 | Yes |
| Service comparison | `service-descriptions` | category_id, price_range | 10 | Yes |
| Review search | `reviews` | provider_id, rating, sentiment | 10 | Yes |
| Similar conversations | `chat-history` | intent, resolved, agent_used | 5 | Yes |
| Conversation learning | `chat-history` | intent, satisfaction_score | 20 | Yes |

### 4.2 Performance Targets

- **Query Latency**: <100ms (warm), <200ms (cold start)
- **Accuracy**: >0.85 similarity score for relevant results
- **Recall**: >90% for top-5 results
- **Throughput**: 100+ queries/second

---

## 5. Implementation Plan {#implementation-plan}

### Phase 1: Core Setup (Week 1)
1. ✅ Pinecone service implementation
2. ✅ Embedding service implementation
3. ⏭️ Create all namespaces in Pinecone
4. ⏭️ Implement metadata validation schemas

### Phase 2: Document Preparation (Week 2)
1. Create policy documents (Task 2)
2. Extract service catalog data from MySQL
3. Create FAQ content
4. Prepare training materials

### Phase 3: Ingestion Pipeline (Week 3)
1. Implement document chunking
2. Create namespace-specific ingestion scripts
3. Validate metadata for each namespace
4. Bulk upload documents

### Phase 4: Testing & Optimization (Week 4)
1. Test search across all namespaces
2. Validate metadata filtering
3. Optimize chunk sizes
4. Performance tuning

---

## Next Steps

1. **Immediate**: Create policy documents (Task 2)
2. **Then**: Implement namespace creation script
3. **Then**: Build document ingestion pipeline
4. **Finally**: Test and validate search functionality


