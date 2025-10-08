# Phase 7: Remaining Tasks

**Date**: 2025-10-07  
**Current Status**: Phase 7.1 & 7.2 Complete ✅  
**Next**: Phase 7.3 Document Ingestion

---

## ✅ Completed Tasks

### Phase 7.1: Pinecone Configuration (COMPLETE)
- ✅ Set up Pinecone client (Serverless, us-east-1, AWS)
- ✅ Create Pinecone index for documents (auto-creation)
- ✅ Configure index dimensions (384 for all-MiniLM-L6-v2)
- ✅ Set up metadata schema (flexible support)
- ✅ Implement connection health check
- ✅ Add index statistics retrieval
- ✅ Implement namespace support

**Files**: `backend/src/rag/vector_store/pinecone_service.py`

### Phase 7.2: Embedding Service (COMPLETE)
- ✅ Create embedding service using sentence-transformers/all-MiniLM-L6-v2
- ✅ Implement batch embedding generation
- ✅ Create embedding utility functions (similarity, batch similarity)
- ✅ Add error handling and retries
- ✅ Implement singleton pattern
- ✅ Add CPU/GPU device support
- ✅ Add normalized embeddings

**Files**: `backend/src/rag/embeddings/embedding_service.py`

### Testing & Documentation (COMPLETE)
- ✅ Comprehensive test suite
- ✅ Setup documentation (401 lines)
- ✅ Module README (356 lines)
- ✅ Quick reference guide
- ✅ Implementation summary

---

## 🚧 Remaining Tasks

### Phase 7.3: Document Ingestion (TODO)

#### 1. Document Chunking Service
**Priority**: HIGH  
**Estimated Time**: 4-6 hours

**Tasks**:
- [ ] Create `backend/src/rag/chunking/chunking_service.py`
- [ ] Implement text splitter (by tokens, sentences, paragraphs)
- [ ] Add overlap strategy for context preservation
- [ ] Support multiple document types (PDF, TXT, DOCX, HTML)
- [ ] Add metadata extraction from documents
- [ ] Implement chunk size optimization (256 tokens for all-MiniLM-L6-v2)
- [ ] Add chunking tests

**Key Considerations**:
- Max sequence length: 256 tokens
- Optimal chunk size: 200-250 tokens with 20-50 token overlap
- Preserve context across chunks
- Extract and preserve metadata (title, source, page number, etc.)

**Dependencies**:
```python
# Add to requirements.txt
langchain-text-splitters==0.3.2
pypdf2==3.0.1
python-docx==1.1.2
beautifulsoup4==4.12.3
```

#### 2. Document Upload Endpoint
**Priority**: HIGH  
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `POST /api/v1/documents/upload` endpoint
- [ ] Implement file validation (type, size)
- [ ] Add document processing pipeline
- [ ] Store original document metadata in MySQL
- [ ] Generate and store embeddings in Pinecone
- [ ] Return document ID and processing status
- [ ] Add upload tests

**Endpoint Spec**:
```python
POST /api/v1/documents/upload
Content-Type: multipart/form-data

Request:
- file: File (required)
- category: str (optional)
- namespace: str (optional, default: "default")
- metadata: JSON (optional)

Response:
{
    "document_id": "uuid",
    "filename": "document.pdf",
    "chunks_created": 15,
    "vectors_stored": 15,
    "status": "completed"
}
```

#### 3. Document Metadata Storage (MySQL)
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Create `documents` table in MySQL
- [ ] Create `document_chunks` table
- [ ] Create SQLAlchemy models
- [ ] Create Alembic migration
- [ ] Implement document repository
- [ ] Add CRUD operations
- [ ] Add tests

**Schema**:
```sql
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    category VARCHAR(100),
    namespace VARCHAR(100) DEFAULT 'default',
    total_chunks INT,
    metadata JSON,
    uploaded_by VARCHAR(36),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_namespace (namespace),
    INDEX idx_uploaded_by (uploaded_by)
);

CREATE TABLE document_chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_tokens INT,
    vector_id VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document_id (document_id),
    INDEX idx_vector_id (vector_id)
);
```

#### 4. Document Search Endpoint
**Priority**: HIGH  
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Create `POST /api/v1/documents/search` endpoint
- [ ] Implement semantic search with Pinecone
- [ ] Add metadata filtering
- [ ] Add result ranking and formatting
- [ ] Include source document information
- [ ] Add pagination support
- [ ] Add search tests

**Endpoint Spec**:
```python
POST /api/v1/documents/search
Content-Type: application/json

Request:
{
    "query": "What is the refund policy?",
    "top_k": 5,
    "namespace": "policies",
    "filter": {
        "category": "customer_service"
    }
}

Response:
{
    "results": [
        {
            "chunk_id": "uuid",
            "document_id": "uuid",
            "document_name": "refund_policy.pdf",
            "score": 0.89,
            "text": "Our refund policy states...",
            "metadata": {
                "page": 2,
                "category": "customer_service"
            }
        }
    ],
    "total_results": 5,
    "query_time_ms": 120
}
```

---

### Phase 7.4: Vector Search Enhancements (TODO)

#### 1. Hybrid Search
**Priority**: MEDIUM  
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Implement BM25 keyword search
- [ ] Combine dense (semantic) + sparse (keyword) search
- [ ] Add score fusion strategies (RRF, weighted)
- [ ] Add hybrid search endpoint
- [ ] Add tests

#### 2. Reranking
**Priority**: LOW  
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Integrate cross-encoder model for reranking
- [ ] Add reranking to search pipeline
- [ ] Optimize for latency
- [ ] Add tests

#### 3. Search Result Caching
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Implement Redis caching for search results
- [ ] Add cache key generation (query + filters)
- [ ] Set appropriate TTL
- [ ] Add cache invalidation on document updates
- [ ] Add tests

---

## 📋 Implementation Order

### Week 1: Core Document Ingestion
1. **Day 1-2**: Document Chunking Service
   - Implement text splitter
   - Add document type support
   - Write tests

2. **Day 3**: MySQL Schema & Models
   - Create tables
   - Create models
   - Run migration

3. **Day 4-5**: Document Upload Endpoint
   - Implement upload API
   - Integrate chunking + embedding + storage
   - Write tests

### Week 2: Search & Enhancements
4. **Day 1-2**: Document Search Endpoint
   - Implement search API
   - Add filtering and ranking
   - Write tests

5. **Day 3**: Search Result Caching
   - Implement Redis caching
   - Add cache invalidation
   - Write tests

6. **Day 4-5**: Hybrid Search (Optional)
   - Implement BM25
   - Add score fusion
   - Write tests

---

## 🎯 Success Criteria

### Phase 7.3 Complete When:
- ✅ Users can upload documents (PDF, TXT, DOCX)
- ✅ Documents are automatically chunked and embedded
- ✅ Chunks are stored in Pinecone with metadata
- ✅ Document metadata is stored in MySQL
- ✅ Users can search documents semantically
- ✅ Search results include source information
- ✅ All tests pass

### Phase 7.4 Complete When:
- ✅ Hybrid search is implemented
- ✅ Search results are cached
- ✅ Reranking improves result quality (optional)
- ✅ All tests pass

---

## 📚 Resources

### Libraries to Add
```bash
# Document processing
langchain-text-splitters==0.3.2
pypdf2==3.0.1
python-docx==1.1.2
beautifulsoup4==4.12.3
lxml==5.1.0

# Hybrid search (optional)
rank-bm25==0.2.2
```

### Documentation References
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Pinecone Metadata Filtering](https://docs.pinecone.io/guides/data/filter-with-metadata)
- [Hybrid Search Best Practices](https://www.pinecone.io/learn/hybrid-search-intro/)

---

## 🚀 Next Steps

1. **Immediate**: Start with Document Chunking Service
2. **Then**: Create MySQL schema and models
3. **Then**: Implement Document Upload Endpoint
4. **Finally**: Implement Document Search Endpoint

**Estimated Total Time**: 2-3 weeks for complete Phase 7 implementation

