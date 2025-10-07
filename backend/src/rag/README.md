# RAG (Retrieval-Augmented Generation) Module

## Overview

This module provides the core RAG functionality for the ConvergeAI project, including:
- Text embedding generation using Sentence Transformers
- Vector storage and retrieval using Pinecone
- Document chunking and processing
- Semantic search capabilities

## Architecture

```
rag/
├── embeddings/              # Embedding generation
│   ├── __init__.py
│   └── embedding_service.py # Sentence Transformers service
├── vector_store/            # Vector database
│   ├── __init__.py
│   └── pinecone_service.py  # Pinecone integration
├── retrieval/               # Retrieval strategies
│   └── __init__.py
└── prompts/                 # RAG prompts
    └── __init__.py
```

## Components

### 1. Embedding Service

**File**: `embeddings/embedding_service.py`

**Purpose**: Generate text embeddings using sentence-transformers/all-MiniLM-L6-v2

**Key Features**:
- 384-dimensional embeddings
- Batch processing support
- Similarity calculation
- CPU/GPU support
- Normalized embeddings for cosine similarity

**Usage**:
```python
from src.rag.embeddings import get_embedding_service

# Get singleton instance
embedding_service = get_embedding_service()

# Generate embeddings
embedding = embedding_service.embed_text("Hello world")
embeddings = embedding_service.embed_texts(["Text 1", "Text 2"])

# Calculate similarity
similarity = embedding_service.similarity(emb1, emb2)
```

### 2. Pinecone Service

**File**: `vector_store/pinecone_service.py`

**Purpose**: Manage vector storage and retrieval in Pinecone

**Key Features**:
- Serverless Pinecone index (us-east-1, AWS)
- Automatic index creation
- Document upsert with auto-embedding
- Text-based querying
- Metadata filtering
- Namespace support

**Usage**:
```python
from src.rag.vector_store import get_pinecone_service

# Get singleton instance
pinecone_service = get_pinecone_service()

# Upsert documents
documents = [
    {"id": "doc1", "text": "Content...", "category": "tech"}
]
pinecone_service.upsert_documents(documents, namespace="kb")

# Query by text
results = pinecone_service.query_by_text(
    query_text="What is AI?",
    top_k=5,
    namespace="kb"
)
```

## Configuration

### Environment Variables

```bash
# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=100
EMBEDDING_DEVICE=cpu
EMBEDDING_NORMALIZE=True

# Pinecone Configuration
PINECONE_API_KEY=your_api_key
PINECONE_INDEX_NAME=convergeai-documents
PINECONE_DIMENSION=384
PINECONE_METRIC=cosine
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_CAPACITY_MODE=serverless
```

### Settings Access

```python
from src.core.config.settings import settings

# Access configuration
model_name = settings.EMBEDDING_MODEL
dimension = settings.EMBEDDING_DIMENSION
index_name = settings.PINECONE_INDEX_NAME
```

## Model Information

### sentence-transformers/all-MiniLM-L6-v2

**Specifications**:
- **Dimensions**: 384
- **Max Sequence Length**: 256 tokens
- **Model Size**: ~90MB
- **Speed**: ~2000 sentences/second (CPU)
- **Quality**: Excellent for semantic search

**Advantages**:
- Fast inference
- Compact size
- No API costs
- Proven performance
- Wide adoption

**Use Cases**:
- Semantic search
- Document similarity
- Question answering
- Clustering
- Classification

## Pinecone Serverless

**Specifications**:
- **Type**: Serverless
- **Cloud**: AWS
- **Region**: us-east-1
- **Metric**: Cosine similarity
- **Dimension**: 384

**Advantages**:
- Auto-scaling
- Pay-per-use pricing
- No infrastructure management
- Fast cold start
- High availability

**Cost Estimation**:
- Storage: $0.25/GB/month
- Read units: $0.20/million
- Write units: $2.00/million

## Testing

### Run Tests

```bash
cd backend
source venv/bin/activate
python tests/test_embedding_pinecone.py
```

### Test Coverage

The test suite covers:
1. Configuration validation
2. Embedding generation (single & batch)
3. Similarity calculation
4. Pinecone connection
5. Document upsert
6. Text-based querying
7. Health checks

## Best Practices

### 1. Use Singleton Pattern

```python
# ✅ Good: Use singleton
from src.rag.embeddings import get_embedding_service
service = get_embedding_service()

# ❌ Bad: Create new instances
from src.rag.embeddings import EmbeddingService
service = EmbeddingService()  # Don't do this
```

### 2. Batch Processing

```python
# ✅ Good: Batch processing
texts = ["text1", "text2", ..., "text100"]
embeddings = embedding_service.embed_texts(texts)

# ❌ Bad: One by one
embeddings = [embedding_service.embed_text(t) for t in texts]
```

### 3. Use Namespaces

```python
# ✅ Good: Organize by namespace
pinecone_service.upsert_documents(docs, namespace="policies")
pinecone_service.upsert_documents(docs, namespace="faqs")

# ❌ Bad: Mix everything in default namespace
pinecone_service.upsert_documents(docs)
```

### 4. Metadata Filtering

```python
# ✅ Good: Use metadata filters
results = pinecone_service.query_by_text(
    query_text="pricing",
    filter={"category": "docs", "version": "2.0"}
)

# ❌ Bad: Query everything and filter in code
results = pinecone_service.query_by_text(query_text="pricing")
filtered = [r for r in results if r['metadata']['category'] == 'docs']
```

### 5. Error Handling

```python
# ✅ Good: Handle errors
try:
    results = pinecone_service.query_by_text(query)
except Exception as e:
    logger.error(f"Query failed: {e}")
    # Fallback logic
```

## Performance Tips

### 1. GPU Acceleration

```bash
# Install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Update config
EMBEDDING_DEVICE=cuda
```

### 2. Batch Size Tuning

```python
# Adjust based on memory
EMBEDDING_BATCH_SIZE=32   # Low memory
EMBEDDING_BATCH_SIZE=100  # Default
EMBEDDING_BATCH_SIZE=256  # High memory
```

### 3. Caching

```python
# Cache embeddings in Redis
from src.core.cache import get_redis_client

async def get_cached_embedding(text: str):
    redis = get_redis_client()
    cache_key = f"emb:{hash(text)}"
    
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    embedding = embedding_service.embed_text(text)
    await redis.set(cache_key, json.dumps(embedding), ex=86400)
    return embedding
```

## Troubleshooting

### Model Download Issues

```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Dimension Mismatch

Ensure both settings match:
```bash
EMBEDDING_DIMENSION=384
PINECONE_DIMENSION=384
```

### Connection Timeout

Check Pinecone API key and network:
```python
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
print(pc.list_indexes())
```

## Future Enhancements

### Planned Features

1. **Hybrid Search**: Combine dense and sparse embeddings
2. **Reranking**: Add cross-encoder reranking
3. **Document Chunking**: Smart text splitting strategies
4. **Multi-modal**: Support for image embeddings
5. **Query Expansion**: Automatic query enhancement
6. **Caching Layer**: Redis-based embedding cache
7. **Monitoring**: Track embedding quality metrics

### Roadmap

- [ ] Implement document chunking service
- [ ] Add reranking with cross-encoders
- [ ] Create retrieval strategies (dense, sparse, hybrid)
- [ ] Add embedding quality metrics
- [ ] Implement query expansion
- [ ] Add multi-language support
- [ ] Create RAG evaluation framework

## References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## Support

For issues or questions:
1. Check the main documentation: `backend/docs/EMBEDDING_VECTOR_STORE_SETUP.md`
2. Run the test suite: `python tests/test_embedding_pinecone.py`
3. Review logs in `backend/logs/app.log`
4. Check Pinecone dashboard for index status

