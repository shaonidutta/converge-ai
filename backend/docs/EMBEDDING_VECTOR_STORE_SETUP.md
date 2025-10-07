# Embedding & Vector Store Configuration

## Overview

This document describes the embedding model and vector database configuration for the ConvergeAI project.

## Configuration Summary

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Type**: Dense embeddings
- **Framework**: Sentence Transformers (HuggingFace)

### Vector Database
- **Provider**: Pinecone
- **Type**: Serverless
- **Region**: us-east-1
- **Cloud**: AWS
- **Metric**: Cosine similarity
- **Capacity Mode**: Serverless

## Why sentence-transformers/all-MiniLM-L6-v2?

### Advantages
1. **Optimal Balance**: Great balance between speed, size, and quality
2. **Compact Size**: Only 384 dimensions (vs 768 for larger models)
3. **Fast Inference**: Lightweight model enables quick embedding generation
4. **Cost-Effective**: Smaller dimensions = lower storage costs in Pinecone
5. **Proven Performance**: Widely used and tested in production
6. **No API Costs**: Runs locally, no per-request API charges

### Performance Characteristics
- **Speed**: ~2000 sentences/second on CPU
- **Quality**: Excellent for semantic search and similarity tasks
- **Memory**: ~90MB model size
- **Latency**: <10ms per sentence on modern CPUs

### Comparison with Alternatives

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ | ⭐⭐⭐ | **Production (Chosen)** |
| all-mpnet-base-v2 | 768 | ⚡⚡ | ⭐⭐⭐⭐ | Higher quality needed |
| text-embedding-004 (Google) | 768 | ⚡ | ⭐⭐⭐⭐ | API-based, costs per call |
| text-embedding-3-small (OpenAI) | 1536 | ⚡ | ⭐⭐⭐⭐ | API-based, costs per call |

## Pinecone Serverless Configuration

### Why Serverless?
1. **Cost-Effective**: Pay only for storage and operations
2. **Auto-Scaling**: Automatically scales with demand
3. **No Infrastructure**: No pod management required
4. **Fast Cold Start**: Quick initialization
5. **Regional Availability**: Available in us-east-1

### Specifications
```python
{
    "name": "convergeai-documents",
    "dimension": 384,
    "metric": "cosine",
    "spec": {
        "serverless": {
            "cloud": "aws",
            "region": "us-east-1"
        }
    }
}
```

### Cost Estimation (Serverless)
- **Storage**: $0.25 per GB/month
- **Read Units**: $0.20 per million read units
- **Write Units**: $2.00 per million write units

**Example**: 100K documents (384 dims each)
- Storage: ~150MB = $0.04/month
- 1M queries/month: ~$0.20/month
- **Total**: ~$0.24/month

## Environment Configuration

### Required Environment Variables

```bash
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=convergeai-documents
PINECONE_DIMENSION=384
PINECONE_METRIC=cosine
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_CAPACITY_MODE=serverless

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=100
EMBEDDING_DEVICE=cpu  # or cuda for GPU
EMBEDDING_NORMALIZE=True
```

## Usage Examples

### 1. Generate Embeddings

```python
from src.rag.embeddings import get_embedding_service

# Get embedding service (singleton)
embedding_service = get_embedding_service()

# Embed single text
text = "What is machine learning?"
embedding = embedding_service.embed_text(text)
print(f"Embedding dimension: {len(embedding)}")  # 384

# Embed multiple texts
texts = [
    "Machine learning is a subset of AI",
    "Deep learning uses neural networks",
    "Natural language processing handles text"
]
embeddings = embedding_service.embed_texts(texts)
print(f"Generated {len(embeddings)} embeddings")

# Calculate similarity
similarity = embedding_service.similarity(embeddings[0], embeddings[1])
print(f"Similarity: {similarity:.4f}")
```

### 2. Store Documents in Pinecone

```python
from src.rag.vector_store import get_pinecone_service

# Get Pinecone service (singleton)
pinecone_service = get_pinecone_service()

# Prepare documents
documents = [
    {
        "id": "doc-1",
        "text": "Machine learning is a method of data analysis...",
        "category": "AI",
        "source": "knowledge_base"
    },
    {
        "id": "doc-2",
        "text": "Deep learning is a subset of machine learning...",
        "category": "AI",
        "source": "knowledge_base"
    }
]

# Upsert documents (embeddings generated automatically)
result = pinecone_service.upsert_documents(
    documents=documents,
    namespace="knowledge_base"
)
print(f"Upserted {result['upserted_count']} documents")
```

### 3. Query Similar Documents

```python
# Query by text (embedding generated automatically)
results = pinecone_service.query_by_text(
    query_text="What is deep learning?",
    top_k=5,
    namespace="knowledge_base",
    filter={"category": "AI"}  # Optional metadata filter
)

# Process results
for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.4f}")
    print(f"   ID: {result['id']}")
    print(f"   Preview: {result['metadata']['text_preview']}")
```

### 4. Health Check

```python
# Check if services are healthy
is_healthy = pinecone_service.health_check()
print(f"Pinecone service healthy: {is_healthy}")

# Get index statistics
stats = pinecone_service.get_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Dimension: {stats['dimension']}")
```

## Testing

### Run Integration Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run tests
python tests/test_embedding_pinecone.py
```

### Expected Output
```
================================================================================
EMBEDDING & PINECONE INTEGRATION TEST
================================================================================

TESTING CONFIGURATION
✅ Pinecone and Embedding dimensions match!

TESTING EMBEDDING SERVICE
✅ Embedding service loaded successfully!
✅ Similarity scores make sense!

TESTING PINECONE SERVICE
✅ Pinecone service initialized successfully!
✅ Pinecone service is healthy!
✅ Upserted 3 documents

================================================================================
TEST SUMMARY
================================================================================
Configuration: ✅ PASSED
Embedding Service: ✅ PASSED
Pinecone Service: ✅ PASSED

🎉 ALL TESTS PASSED!
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (FastAPI Routes, Services, Agents)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Layer                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Embedding Service   │    │  Pinecone Service    │      │
│  │  (all-MiniLM-L6-v2) │◄───┤  (Vector Store)      │      │
│  │  - 384 dimensions    │    │  - Serverless        │      │
│  │  - Local inference   │    │  - us-east-1         │      │
│  └──────────────────────┘    └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Services                           │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  HuggingFace Hub     │    │  Pinecone Cloud      │      │
│  │  (Model Download)    │    │  (Vector Storage)    │      │
│  └──────────────────────┘    └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### 1. Batch Processing
```python
# ✅ Good: Process in batches
texts = [...]  # 1000 texts
embeddings = embedding_service.embed_texts(texts)  # Efficient

# ❌ Bad: Process one by one
embeddings = [embedding_service.embed_text(t) for t in texts]  # Slow
```

### 2. Caching
```python
# Cache frequently used embeddings in Redis
from src.core.cache import get_redis_client

redis = get_redis_client()
cache_key = f"embedding:{text_hash}"

# Check cache first
cached = await redis.get(cache_key)
if cached:
    embedding = json.loads(cached)
else:
    embedding = embedding_service.embed_text(text)
    await redis.set(cache_key, json.dumps(embedding), ex=86400)
```

### 3. Metadata Filtering
```python
# Use metadata filters for efficient queries
results = pinecone_service.query_by_text(
    query_text="pricing information",
    filter={
        "category": "documentation",
        "version": "2.0",
        "language": "en"
    }
)
```

### 4. Namespace Organization
```python
# Organize vectors by namespace
namespaces = {
    "knowledge_base": "General knowledge articles",
    "policies": "Company policies and procedures",
    "faqs": "Frequently asked questions",
    "products": "Product documentation"
}

# Query specific namespace
results = pinecone_service.query_by_text(
    query_text="refund policy",
    namespace="policies"
)
```

## Troubleshooting

### Issue: Dimension Mismatch
**Error**: `ValueError: Dimension mismatch`

**Solution**: Ensure PINECONE_DIMENSION matches EMBEDDING_DIMENSION (both should be 384)

### Issue: Model Download Fails
**Error**: `OSError: Can't load model`

**Solution**: 
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Issue: Pinecone Connection Timeout
**Error**: `TimeoutError: Connection timeout`

**Solution**: Check API key and network connectivity
```python
# Test connection
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
print(pc.list_indexes())
```

## Migration from Other Models

### From Google text-embedding-004 (768 dims)

1. Update configuration:
```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
PINECONE_DIMENSION=384
```

2. Create new Pinecone index with 384 dimensions

3. Re-embed and re-index all documents

4. Update application code to use new services

## Performance Optimization

### GPU Acceleration (Optional)
```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update configuration
EMBEDDING_DEVICE=cuda
```

### Batch Size Tuning
```python
# Adjust based on available memory
EMBEDDING_BATCH_SIZE=32   # Low memory
EMBEDDING_BATCH_SIZE=100  # Medium memory (default)
EMBEDDING_BATCH_SIZE=256  # High memory
```

## References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Pinecone Serverless Documentation](https://docs.pinecone.io/guides/indexes/understanding-indexes#serverless-indexes)
- [Pinecone Python SDK](https://docs.pinecone.io/reference/python-sdk)

