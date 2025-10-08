# Embedding & Vector Store Quick Reference

## Configuration Summary

```
Model: sentence-transformers/all-MiniLM-L6-v2
Dimension: 384
Vector DB: Pinecone Serverless
Region: us-east-1 (AWS)
Metric: Cosine
```

## Quick Start

### 1. Set Environment Variables

```bash
# Required
PINECONE_API_KEY=your_api_key
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
PINECONE_DIMENSION=384
```

### 2. Generate Embeddings

```python
from src.rag.embeddings import get_embedding_service

service = get_embedding_service()
embedding = service.embed_text("Hello world")
```

### 3. Store Documents

```python
from src.rag.vector_store import get_pinecone_service

service = get_pinecone_service()
docs = [{"id": "1", "text": "Content...", "meta": "data"}]
service.upsert_documents(docs, namespace="kb")
```

### 4. Query

```python
results = service.query_by_text(
    query_text="What is AI?",
    top_k=5,
    namespace="kb"
)
```

## Common Operations

### Embedding Service

```python
from src.rag.embeddings import get_embedding_service
emb = get_embedding_service()

# Single text
vec = emb.embed_text("text")

# Batch
vecs = emb.embed_texts(["text1", "text2"])

# Similarity
sim = emb.similarity(vec1, vec2)

# Batch similarity
sims = emb.batch_similarity(query_vec, doc_vecs)

# Model info
info = emb.get_model_info()
```

### Pinecone Service

```python
from src.rag.vector_store import get_pinecone_service
pc = get_pinecone_service()

# Upsert vectors
vectors = [("id1", [0.1, 0.2, ...], {"key": "value"})]
pc.upsert_vectors(vectors, namespace="ns")

# Upsert documents (auto-embed)
docs = [{"id": "1", "text": "...", "category": "tech"}]
pc.upsert_documents(docs, namespace="ns")

# Query by vector
results = pc.query(query_vector, top_k=5, namespace="ns")

# Query by text (auto-embed)
results = pc.query_by_text("query", top_k=5, namespace="ns")

# With filter
results = pc.query_by_text(
    "query",
    filter={"category": "tech"},
    namespace="ns"
)

# Delete
pc.delete(ids=["id1", "id2"], namespace="ns")

# Stats
stats = pc.get_index_stats()

# Health check
healthy = pc.health_check()
```

## Testing

```bash
cd backend
source venv/bin/activate
python tests/test_embedding_pinecone.py
```

## Troubleshooting

### Dimension Mismatch
```bash
# Ensure both are 384
EMBEDDING_DIMENSION=384
PINECONE_DIMENSION=384
```

### Model Download
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Connection Issues
```python
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
print(pc.list_indexes())
```

## Best Practices

✅ Use singleton pattern: `get_embedding_service()`  
✅ Batch process: `embed_texts(texts)` not loop  
✅ Use namespaces: Organize vectors logically  
✅ Use metadata filters: Efficient querying  
✅ Cache embeddings: Store in Redis for reuse  

❌ Don't create new instances each time  
❌ Don't process one by one  
❌ Don't mix everything in default namespace  
❌ Don't filter in code after query  

## Performance Tips

```python
# GPU acceleration
EMBEDDING_DEVICE=cuda

# Batch size tuning
EMBEDDING_BATCH_SIZE=256  # High memory

# Caching
from src.core.cache import get_redis_client
# Cache embeddings in Redis
```

## Documentation

- Setup Guide: `backend/docs/EMBEDDING_VECTOR_STORE_SETUP.md`
- Module README: `backend/src/rag/README.md`
- Implementation: `backend/.dev-logs/EMBEDDING_VECTOR_STORE_IMPLEMENTATION.md`

## Support

1. Check logs: `backend/logs/app.log`
2. Run tests: `python tests/test_embedding_pinecone.py`
3. Check Pinecone dashboard
4. Review documentation

