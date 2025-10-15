# Pinecone Collections - Final Structure

**Project**: ConvergeAI  
**Date**: 2025-10-08  
**Status**: ✅ FINALIZED

---

## 🗂️ PINECONE INDEX CONFIGURATION

### Index Details:
- **Index Name**: `convergeai-documents`
- **Dimensions**: 384 (sentence-transformers/all-MiniLM-L6-v2)
- **Metric**: Cosine similarity
- **Cloud Provider**: AWS
- **Region**: us-east-1
- **Type**: Serverless

---

## 📊 NAMESPACE STRUCTURE

We will use **3 namespaces** within a single Pinecone index:

```
convergeai-documents (Index)
├── documents (Namespace)
├── service-descriptions (Namespace)
└── reviews (Namespace)
```

---

## 📁 NAMESPACE 1: `documents`

### Purpose:
Store policy documents, terms & conditions, FAQs, and guides for semantic search.

### Data Sources:
- Terms & Conditions PDF
- Privacy Policy PDF
- Refund & Cancellation Policy PDF
- FAQs (future)
- User Guides (future)

### Vector ID Format:
```
doc_{document_type}_{document_id}_chunk_{chunk_index}

Examples:
- doc_terms_001_chunk_0
- doc_privacy_002_chunk_5
- doc_faq_003_chunk_2
```

### Metadata Structure:
```python
{
    # Identifiers
    "vector_id": "doc_terms_001_chunk_0",
    "document_id": "001",
    "document_type": "terms",  # terms, privacy, refund, faq, guide
    
    # Content
    "title": "Terms and Conditions",
    "section": "5. BOOKINGS",
    "subsection": "Rescheduling",
    "chunk_text": "Full text of this chunk...",
    "chunk_index": 0,
    "total_chunks": 15,
    
    # Classification
    "applicability": "customer",  # customer, provider, both
    "category": "policy",  # policy, faq, guide, legal
    "tags": ["booking", "rescheduling", "cancellation"],
    
    # Versioning
    "version": "1.0",
    "effective_date": "2025-01-01",
    "last_updated": "2025-01-01T00:00:00Z",
    
    # Status
    "is_active": true,
    "language": "en"
}
```

### Use Cases:
1. **Policy Queries**: "What is the cancellation policy?"
2. **Terms Lookup**: "Can I reschedule my booking?"
3. **FAQ Search**: "How do refunds work?"
4. **Compliance**: Legal and policy information retrieval

### Estimated Vectors: 500-1,000

---

## 📁 NAMESPACE 2: `service-descriptions`

### Purpose:
Store detailed service descriptions at **SUBCATEGORY LEVEL** for semantic search and service discovery. **Scalable approach - no rate_card_ids stored.**

### Data Sources:
- Service descriptions at subcategory level (76 subcategories)
- Linked to MySQL tables: `subcategories`, `categories`
- Rate cards fetched from MySQL based on category + subcategory

### Vector ID Format:
```
service_{category_id}_{subcategory_id}_chunk_{chunk_index}

Examples:
- service_2_9_chunk_0      # Appliance Repair > AC Repair
- service_2_9_chunk_1
- service_3_17_chunk_0     # Plumbing > Tap Repair
```

### Metadata Structure:
```python
{
    # Identifiers (SCALABLE - Only category/subcategory)
    "vector_id": "service_2_9_chunk_0",
    "subcategory_id": 9,           # FOREIGN KEY to subcategories table
    "category_id": 2,              # FOREIGN KEY to categories table

    # Names (for display and filtering)
    "subcategory_name": "AC Repair",
    "category_name": "Appliance Repair",
    "category_slug": "appliance-repair",
    "subcategory_slug": "ac-repair",

    # Content
    "chunk_text": "Expert AC repair service for split and window AC units. Our professional technicians diagnose and fix all AC issues including cooling problems, gas leaks, compressor issues, and electrical faults...",
    "chunk_index": 0,
    "total_chunks": 3,
    "section": "service_overview",  # service_overview, benefits, process, requirements

    # Service Classification
    "service_type": "b2c",  # b2c, b2b
    "service_category": "repair",  # repair, installation, cleaning, beauty, moving
    "tags": ["ac", "repair", "appliance", "cooling", "split-ac", "window-ac", "hvac"],

    # General Info (not specific to rate cards)
    "has_variants": true,
    "typical_duration": "2-3 hours",
    "requires_pincode_check": true,

    # Availability
    "is_active": true,

    # Metadata for search
    "language": "en",
    "last_updated": "2025-01-01T00:00:00Z"
}
```

### Integration with MySQL:

#### Flow (REVISED - Scalable):
1. **Search Vector DB** → Get `category_id` + `subcategory_id` from metadata
2. **Query MySQL** → Get ALL rate cards for that subcategory with pricing
3. **Return** → Description + All available pricing variants

#### SQL Query After Vector Search:
```sql
-- Get all rate cards for matched subcategories
SELECT
    rc.id,
    rc.name,
    rc.price,
    rc.strike_price,
    rc.is_active,
    s.id as subcategory_id,
    s.name as subcategory_name,
    c.id as category_id,
    c.name as category_name,
    GROUP_CONCAT(DISTINCT rcp.pincode) as available_pincodes
FROM rate_cards rc
JOIN subcategories s ON rc.subcategory_id = s.id
JOIN categories c ON rc.category_id = c.id
LEFT JOIN rate_card_pincodes rcp ON rc.id = rcp.rate_card_id
WHERE s.id IN (9, 11, 10)  -- Subcategory IDs from Vector DB
  AND rc.is_active = TRUE
GROUP BY rc.id
ORDER BY rc.price ASC;
```

### Use Cases:
1. **Service Discovery**: "Show me AC repair services" → Returns AC Repair subcategory → MySQL fetches all AC repair rate cards
2. **Semantic Search**: "My AC is not cooling properly" → Matches AC Repair, AC Gas Refilling subcategories → MySQL returns all variants
3. **Price Comparison**: Get description from Vector DB, all pricing variants from MySQL
4. **Booking Flow**: Search → Get subcategory → Fetch all rate cards → Display options → Book

### Scalability Benefits:
- ✅ **Fixed vector count**: Only 76 subcategories (not millions of rate cards)
- ✅ **Easy updates**: Update subcategory description once, applies to all rate cards
- ✅ **Flexible pricing**: Add/remove rate cards in MySQL without touching Vector DB
- ✅ **Cost-effective**: Minimal vectors, maximum flexibility

### Estimated Vectors: 200-500 (76 subcategories × 3-5 chunks each)

---

## 📁 NAMESPACE 3: `reviews`

### Purpose:
Store customer reviews for sentiment analysis, service quality insights, and provider ratings. **Uses clear category/subcategory names for easy filtering.**

### Data Sources:
- MySQL `reviews` table (real-time sync)
- Customer feedback and ratings

### Vector ID Format:
```
review_{review_id}

Examples:
- review_12345
- review_67890
```

### Metadata Structure:
```python
{
    # Identifiers (Links to MySQL)
    "vector_id": "review_12345",
    "review_id": 12345,            # PRIMARY KEY in reviews table
    "booking_id": 9876,            # FOREIGN KEY to bookings table
    "user_id": 456,                # FOREIGN KEY to users table
    "provider_id": 201,            # FOREIGN KEY to service_providers table

    # Service Info (CLEAR NAMES - No rate_card_id)
    "subcategory_id": 9,
    "category_id": 2,
    "subcategory_name": "AC Repair",        # ⭐ Clear naming
    "category_name": "Appliance Repair",    # ⭐ Clear naming
    "category_slug": "appliance-repair",
    "subcategory_slug": "ac-repair",

    # Review Content
    "review_text": "Excellent service! The technician was professional and fixed my split AC cooling issue within 2 hours. Highly recommended!",
    "rating": 4.5,                 # 1.0 to 5.0
    "sentiment": "positive",       # positive, neutral, negative
    "sentiment_score": 0.85,       # 0.0 to 1.0

    # Review Classification
    "review_type": "service",      # service, provider, platform
    "verified_booking": true,      # Only verified bookings
    "has_images": false,
    "has_response": false,         # Provider responded

    # Aspects (extracted from review)
    "aspects": {
        "professionalism": 5,
        "timeliness": 4,
        "quality": 5,
        "pricing": 4
    },

    # Tags (auto-extracted from review text)
    "tags": ["professional", "on-time", "quality-work", "polite", "split-ac", "cooling-issue"],

    # Status
    "is_active": true,
    "is_flagged": false,
    "moderation_status": "approved",  # pending, approved, rejected

    # Timestamps
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z",

    # Location
    "city": "Delhi",
    "pincode": "110001"
}
```

### Integration with MySQL:

#### Sync Strategy:
- **Real-time**: New reviews added to Pinecone immediately after MySQL insert
- **Batch**: Nightly sync for updates and deletions
- **Trigger**: MySQL trigger or application-level sync

#### SQL Query for Review Context:
```sql
SELECT 
    r.id,
    r.review_text,
    r.rating,
    r.created_at,
    u.name as customer_name,
    sp.name as provider_name,
    rc.name as service_name,
    b.booking_date
FROM reviews r
JOIN users u ON r.user_id = u.id
JOIN service_providers sp ON r.provider_id = sp.id
JOIN bookings b ON r.booking_id = b.id
JOIN rate_cards rc ON b.rate_card_id = rc.id
WHERE r.id = 12345;
```

### Use Cases:
1. **Review Search**: "Show me reviews about AC repair quality"
2. **Sentiment Analysis**: "What do customers say about our plumbing services?"
3. **Provider Insights**: "Find reviews mentioning 'professional' for provider X"
4. **Service Improvement**: Identify common complaints or praises
5. **Trust Building**: Display relevant reviews during booking

### Estimated Vectors: 5,000-10,000 (grows over time)

---

## 🔄 DATA FLOW DIAGRAMS

### Flow 1: Service Search with Pricing (REVISED - Scalable)
```
User Query: "AC repair for split AC"
    ↓
Vector DB Search (service-descriptions namespace)
    ↓
Returns: [
    {
        category_id: 2,
        subcategory_id: 9,
        category_name: "Appliance Repair",
        subcategory_name: "AC Repair",
        score: 0.92,
        description: "Expert AC repair service for split and window AC..."
    },
    {
        category_id: 2,
        subcategory_id: 11,
        category_name: "Appliance Repair",
        subcategory_name: "AC Gas Refilling",
        score: 0.88,
        description: "AC gas refilling service..."
    }
]
    ↓
Extract: subcategory_ids = [9, 11]
    ↓
MySQL Query: SELECT * FROM rate_cards WHERE subcategory_id IN (9, 11) AND is_active = TRUE
    ↓
Returns: [
    {id: 101, name: "AC Repair - Standard", price: 3532.64, subcategory_id: 9},
    {id: 102, name: "AC Repair - Premium", price: 4408.33, subcategory_id: 9},
    {id: 103, name: "AC Gas Refilling - Basic", price: 1774.69, subcategory_id: 11},
    {id: 104, name: "AC Gas Refilling - Standard", price: 218.33, subcategory_id: 11}
]
    ↓
Combine: Description (Vector DB) + All Pricing Variants (MySQL)
    ↓
Response to User: [
    {
        category: "Appliance Repair",
        subcategory: "AC Repair",
        description: "Expert AC repair service...",
        variants: [
            {id: 101, name: "Standard", price: 3532.64, discount: "21% off"},
            {id: 102, name: "Premium", price: 4408.33, discount: "15% off"}
        ]
    },
    {
        category: "Appliance Repair",
        subcategory: "AC Gas Refilling",
        description: "AC gas refilling service...",
        variants: [
            {id: 103, name: "Basic", price: 1774.69},
            {id: 104, name: "Standard", price: 218.33}
        ]
    }
]
```

### Flow 2: Policy Query
```
User Query: "Can I reschedule my booking?"
    ↓
Vector DB Search (documents namespace)
    ↓
Returns: [
    {
        section: "5. BOOKINGS - Rescheduling",
        chunk_text: "You may request rescheduling...",
        score: 0.95
    }
]
    ↓
Response to User: "Yes, you can reschedule your booking..."
```

### Flow 3: Review-Based Service Discovery (REVISED)
```
User Query: "Show me highly rated AC repair services"
    ↓
Vector DB Search (reviews namespace)
Filter: rating >= 4.5, category_name = "Appliance Repair", subcategory_name = "AC Repair"
    ↓
Returns: [
    {
        review_id: 123,
        subcategory_id: 9,
        category_name: "Appliance Repair",
        subcategory_name: "AC Repair",
        rating: 5.0,
        review_text: "Excellent AC repair service..."
    },
    {
        review_id: 456,
        subcategory_id: 9,
        category_name: "Appliance Repair",
        subcategory_name: "AC Repair",
        rating: 4.8,
        review_text: "Professional and quick..."
    }
]
    ↓
Extract: subcategory_ids = [9]
    ↓
Vector DB Search (service-descriptions namespace)
Filter: subcategory_id = 9
    ↓
Returns: AC Repair description
    ↓
MySQL Query: Get all rate cards for subcategory_id = 9
    ↓
Response: Service with high ratings + description + all pricing variants
```

---

## 📊 SUMMARY TABLE

| Namespace | Purpose | Data Source | Vectors | Links to MySQL | Update Frequency |
|-----------|---------|-------------|---------|----------------|------------------|
| **documents** | Policy & FAQ search | PDF documents | 500-1K | No | Rarely (policy updates) |
| **service-descriptions** | Service discovery | 76 Subcategories | 200-500 | Yes (subcategory_id, category_id) | Monthly (description updates) |
| **reviews** | Review search & sentiment | MySQL reviews | 5K-10K | Yes (review_id, booking_id) | Real-time (new reviews) |
| **TOTAL** | - | - | **5.7K-11.5K** | - | - |

---

## 💾 MYSQL TABLES LINKED TO VECTOR DB

### 1. rate_cards (Fetched via subcategory_id)
```sql
CREATE TABLE rate_cards (
    id BIGINT PRIMARY KEY,              -- NOT stored in Vector DB
    category_id BIGINT,                 -- NOT stored in Vector DB
    subcategory_id BIGINT,              -- Used to fetch rate cards
    name VARCHAR(255),                  -- Fetched from MySQL
    price DECIMAL(10,2),                -- ALWAYS fetch from MySQL
    strike_price DECIMAL(10,2),         -- ALWAYS fetch from MySQL
    is_active BOOLEAN,                  -- Filter in MySQL
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2. reviews (Links to reviews namespace)
```sql
CREATE TABLE reviews (
    id BIGINT PRIMARY KEY,              -- Stored in Vector DB metadata
    booking_id BIGINT,                  -- Stored in Vector DB metadata
    user_id BIGINT,                     -- Stored in Vector DB metadata
    provider_id BIGINT,                 -- Stored in Vector DB metadata
    review_text TEXT,                   -- Embedded in Vector DB
    rating DECIMAL(2,1),                -- Stored in Vector DB metadata
    created_at TIMESTAMP,               -- Stored in Vector DB metadata
    is_active BOOLEAN
);
```

### 3. categories (Reference for filtering)
```sql
CREATE TABLE categories (
    id BIGINT PRIMARY KEY,              -- Stored in Vector DB metadata
    name VARCHAR(255),                  -- Stored in Vector DB metadata
    slug VARCHAR(255),                  -- Stored in Vector DB metadata
    is_active BOOLEAN
);
```

### 4. subcategories (Reference for filtering)
```sql
CREATE TABLE subcategories (
    id BIGINT PRIMARY KEY,              -- Stored in Vector DB metadata
    category_id BIGINT,                 -- Stored in Vector DB metadata
    name VARCHAR(255),                  -- Stored in Vector DB metadata
    slug VARCHAR(255),                  -- Stored in Vector DB metadata
    is_active BOOLEAN
);
```

---

## 🔧 IMPLEMENTATION CHECKLIST

### Phase 1: Setup ✅
- [x] Create Pinecone serverless index
- [x] Configure 3 namespaces
- [x] Set up embedding model (sentence-transformers/all-MiniLM-L6-v2)

### Phase 2: Data Preparation ✅
- [x] Generate 132 service description PDFs
- [x] Convert terms.md to PDF
- [x] Verify all services from MySQL

### Phase 3: Ingestion (Next)
- [ ] Create embedding generation script
- [ ] Ingest documents namespace (3 PDFs)
- [ ] Ingest service-descriptions namespace (132 PDFs)
- [ ] Set up reviews sync pipeline

### Phase 4: Integration (Next)
- [ ] Build Vector DB service layer
- [ ] Create search APIs for each namespace
- [ ] Implement MySQL + Vector DB combined queries
- [ ] Add filtering and ranking logic

### Phase 5: Testing (Next)
- [ ] Test semantic search quality
- [ ] Validate MySQL integration
- [ ] Performance testing
- [ ] Load testing

---

## 💰 COST ESTIMATION (REVISED - More Scalable)

### Pinecone Serverless (AWS us-east-1):

**Storage Cost**:
- 11,500 vectors × 384 dimensions × 4 bytes = 17.7 MB
- Storage: $0.25 per 1M vectors/month
- Cost: (11,500 / 1,000,000) × $0.25 = **$0.003/month**

**Read/Write Cost** (estimated):
- 100K reads/month: ~$0.50
- 10K writes/month: ~$0.10
- **Total: $0.60/month**

**Total Estimated Cost: $0.60-$1.50/month** (extremely affordable!)

**Scalability**: Even with 100K reviews, total cost stays under $3/month!

---

## 🚀 NEXT STEPS

1. **Create Embedding Script** - Generate 384-dim vectors for all PDFs
2. **Ingest to Pinecone** - Upload with proper metadata structure
3. **Build Service Layer** - Python service for Vector DB operations
4. **Create APIs** - Search endpoints for each namespace
5. **Test Integration** - Validate Vector DB + MySQL flow
6. **Deploy** - Production deployment with monitoring

---

**Status**: ✅ **STRUCTURE FINALIZED - READY FOR IMPLEMENTATION**

