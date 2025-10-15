# Vector Database Quick Reference Guide

**Project**: ConvergeAI  
**Last Updated**: 2025-10-08

---

## 🎯 QUICK OVERVIEW

| Aspect | Details |
|--------|---------|
| **Index Name** | `convergeai-documents` |
| **Namespaces** | 3 (documents, service-descriptions, reviews) |
| **Total Vectors** | 5,700-11,500 (scalable to 100K+) |
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 (384 dims) |
| **Cost** | $0.60-$1.50/month (under $3/month at scale) |

---

## 📁 NAMESPACE CHEAT SHEET

### 1. `documents` - Policy & Legal
- **Content**: Terms, Privacy, Refund policies
- **Vectors**: 500-1,000
- **Key Metadata**: `document_id`, `section`, `applicability`
- **MySQL Link**: ❌ No
- **Use Case**: "What's the cancellation policy?"

### 2. `service-descriptions` - Service Catalog
- **Content**: 76 subcategory descriptions (scalable!)
- **Vectors**: 200-500
- **Key Metadata**: `subcategory_id` ⭐, `category_id` ⭐, `subcategory_name`, `category_name`
- **MySQL Link**: ✅ Yes (via subcategory_id to fetch all rate_cards)
- **Use Case**: "Show me AC repair services with prices"

### 3. `reviews` - Customer Feedback
- **Content**: Customer reviews & ratings
- **Vectors**: 5,000-10,000 (grows over time)
- **Key Metadata**: `review_id` ⭐, `booking_id` ⭐, `rating`, `sentiment`, `category_name`, `subcategory_name`
- **MySQL Link**: ✅ Yes (reviews table)
- **Use Case**: "Show highly rated plumbing services"

---

## 🔑 CRITICAL METADATA FIELDS

### service-descriptions namespace:
```python
{
    "subcategory_id": 9,        # ⭐ PRIMARY - Links to MySQL subcategories
    "category_id": 2,           # ⭐ For filtering
    "subcategory_name": "AC Repair",  # ⭐ Clear naming
    "category_name": "Appliance Repair",  # ⭐ Clear naming
    "chunk_text": "Service description...",
    "is_active": true,
    "tags": ["ac", "repair", "appliance", "cooling"]
}
```

### reviews namespace:
```python
{
    "review_id": 12345,         # ⭐ PRIMARY - Links to MySQL
    "booking_id": 9876,         # ⭐ For verification
    "subcategory_id": 9,        # ⭐ Links to service subcategory
    "category_id": 2,           # ⭐ Links to service category
    "subcategory_name": "AC Repair",  # ⭐ Clear naming
    "category_name": "Appliance Repair",  # ⭐ Clear naming
    "rating": 4.5,
    "sentiment": "positive",
    "verified_booking": true
}
```

---

## 🔄 INTEGRATION PATTERNS

### Pattern 1: Service Search with Pricing (REVISED - Scalable)
```python
# Step 1: Search Vector DB
results = pinecone.query(
    namespace="service-descriptions",
    query_vector=embed("AC repair"),
    top_k=5
)

# Step 2: Extract subcategory IDs
subcategory_ids = [r.metadata['subcategory_id'] for r in results]

# Step 3: Query MySQL for ALL rate cards in those subcategories
rate_cards = db.query(RateCard).filter(
    RateCard.subcategory_id.in_(subcategory_ids),
    RateCard.is_active == True
).all()

# Step 4: Group by subcategory and combine
response = []
for result in results:
    subcategory_id = result.metadata['subcategory_id']
    variants = [rc for rc in rate_cards if rc.subcategory_id == subcategory_id]

    response.append({
        'subcategory': result.metadata['subcategory_name'],
        'category': result.metadata['category_name'],
        'description': result.metadata['chunk_text'],
        'variants': [
            {'id': v.id, 'name': v.name, 'price': v.price}
            for v in variants
        ]
    })
```

### Pattern 2: Policy Lookup
```python
# Single step: Search Vector DB only
results = pinecone.query(
    namespace="documents",
    query_vector=embed("Can I reschedule?"),
    top_k=3,
    filter={"document_type": "terms"}
)

# Return directly
response = results[0].metadata['chunk_text']
```

### Pattern 3: Review-Based Discovery
```python
# Step 1: Search reviews
reviews = pinecone.query(
    namespace="reviews",
    query_vector=embed("professional AC repair"),
    top_k=10,
    filter={"rating": {"$gte": 4.5}}
)

# Step 2: Get service IDs
rate_card_ids = [r.metadata['rate_card_id'] for r in reviews]

# Step 3: Get service descriptions
services = pinecone.query(
    namespace="service-descriptions",
    filter={"rate_card_id": {"$in": rate_card_ids}},
    top_k=5
)

# Step 4: Get pricing from MySQL
pricing = db.query(RateCard).filter(
    RateCard.id.in_(rate_card_ids)
).all()
```

---

## 📊 VECTOR ID FORMATS

| Namespace | Format | Example |
|-----------|--------|---------|
| documents | `doc_{type}_{id}_chunk_{n}` | `doc_terms_001_chunk_0` |
| service-descriptions | `service_{category_id}_{subcategory_id}_chunk_{n}` | `service_2_9_chunk_0` |
| reviews | `review_{review_id}` | `review_12345` |

---

## 🔍 COMMON FILTERS

### By Category:
```python
filter={"category_id": 2}  # Appliance Repair
```

### By Service Type:
```python
filter={"service_type": "b2c"}
```

### By Rating:
```python
filter={"rating": {"$gte": 4.5}}
```

### By Active Status:
```python
filter={"is_active": True}
```

### Combined Filters:
```python
filter={
    "category_id": 2,
    "is_active": True,
    "price_range": "medium"
}
```

---

## 💡 BEST PRACTICES

### ✅ DO:
1. **Always fetch pricing from MySQL** - Never rely on Vector DB for prices
2. **Use metadata filters** - Reduce search space before semantic search
3. **Store subcategory/category IDs** - Enable scalable linking to MySQL
4. **Use clear naming** - Store category_name and subcategory_name for easy filtering
5. **Chunk large documents** - Keep chunks 200-500 words
6. **Update reviews in real-time** - Sync new reviews immediately

### ❌ DON'T:
1. **Don't store rate_card_ids** - Millions of rate cards = not scalable
2. **Don't store prices in Vector DB** - They change frequently
3. **Don't skip metadata** - It's critical for filtering
4. **Don't over-chunk** - Too many small chunks reduce context
5. **Don't forget is_active filter** - Always filter inactive items
6. **Don't query MySQL first** - Start with Vector DB for semantic search

---

## 🚀 PERFORMANCE TIPS

### Optimize Search:
```python
# Good: Use filters to reduce search space
results = pinecone.query(
    namespace="service-descriptions",
    query_vector=embed("AC repair"),
    top_k=5,
    filter={"category_id": 2, "is_active": True}  # ✅
)

# Bad: Search everything then filter
results = pinecone.query(
    namespace="service-descriptions",
    query_vector=embed("AC repair"),
    top_k=100  # ❌ Too many results
)
filtered = [r for r in results if r.metadata['category_id'] == 2]
```

### Batch MySQL Queries:
```python
# Good: Single query with IN clause
rate_card_ids = [101, 102, 103, 104, 105]
services = db.query(RateCard).filter(
    RateCard.id.in_(rate_card_ids)  # ✅ Single query
).all()

# Bad: Multiple queries
services = []
for id in rate_card_ids:
    service = db.query(RateCard).filter(RateCard.id == id).first()  # ❌
    services.append(service)
```

---

## 📈 MONITORING METRICS

### Track These:
1. **Search Latency** - Vector DB query time
2. **MySQL Query Time** - After getting IDs
3. **Total Response Time** - End-to-end
4. **Cache Hit Rate** - For frequently searched services
5. **Vector DB Costs** - Monthly Pinecone bill

### Target Performance:
- Vector DB search: < 100ms
- MySQL query: < 50ms
- Total response: < 200ms
- Cache hit rate: > 70%

---

## 🔧 TROUBLESHOOTING

### Issue: Prices don't match
**Solution**: Always fetch from MySQL, never cache prices in Vector DB

### Issue: Inactive services showing
**Solution**: Add `filter={"is_active": True}` to all queries

### Issue: Poor search results
**Solution**: Check embedding quality, adjust top_k, refine metadata

### Issue: Slow queries
**Solution**: Use metadata filters, batch MySQL queries, add caching

### Issue: High costs
**Solution**: Reduce top_k, use filters, optimize chunking strategy

---

## 📞 QUICK COMMANDS

### Search Service:
```python
search_service("AC repair", category_id=2, top_k=5)
```

### Get Service with Price:
```python
get_service_with_pricing(rate_card_id=101)
```

### Search Reviews:
```python
search_reviews("professional service", min_rating=4.5)
```

### Policy Lookup:
```python
search_policy("cancellation", document_type="terms")
```

---

## 📚 RELATED DOCUMENTS

- **Full Structure**: `PINECONE_COLLECTIONS_FINAL_STRUCTURE.md`
- **Documents Summary**: `VECTOR_DATABASE_DOCUMENTS_FINAL.md`
- **Implementation Plan**: `PINECONE_COLLECTIONS_METADATA_PLAN.md`

---

**Status**: ✅ Ready for Implementation

