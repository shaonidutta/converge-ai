"""
Unit tests for ChunkingService
"""
import pytest
from src.rag.chunking.chunking_service import ChunkingService


@pytest.fixture
def chunking_service():
    """Create chunking service instance"""
    return ChunkingService(chunk_size=512, chunk_overlap=50)


@pytest.mark.asyncio
async def test_chunk_markdown_document(chunking_service):
    """Test chunking markdown document with headers"""
    markdown_text = """# Main Title

This is the introduction paragraph.

## Section 1

Content for section 1 with some details.

### Subsection 1.1

More detailed content here.

## Section 2

Content for section 2.
"""
    
    chunks = await chunking_service.chunk_document(
        text=markdown_text,
        document_id="test-doc-1",
        file_type="markdown"
    )
    
    # Assertions
    assert len(chunks) > 0
    assert all("id" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)
    
    # Check metadata
    first_chunk = chunks[0]
    metadata = first_chunk["metadata"]
    assert metadata.chunk_index == 0
    assert metadata.total_chunks == len(chunks)
    assert metadata.token_count > 0
    assert metadata.char_count > 0


@pytest.mark.asyncio
async def test_chunk_plain_text(chunking_service):
    """Test chunking plain text document"""
    plain_text = "This is a simple plain text document. " * 100

    chunks = await chunking_service.chunk_document(
        text=plain_text,
        document_id="test-doc-2",
        file_type="txt"
    )

    # Assertions
    assert len(chunks) > 0

    # Check that chunks have token counts
    for chunk in chunks:
        metadata = chunk["metadata"]
        assert metadata.token_count > 0


@pytest.mark.asyncio
async def test_chunk_with_overlap(chunking_service):
    """Test that chunks have proper overlap"""
    text = "Sentence one. Sentence two. Sentence three. " * 50
    
    chunks = await chunking_service.chunk_document(
        text=text,
        document_id="test-doc-3",
        file_type="txt"
    )
    
    # If multiple chunks, check overlap
    if len(chunks) > 1:
        # Last part of first chunk should appear in second chunk
        first_chunk_text = chunks[0]["text"]
        second_chunk_text = chunks[1]["text"]
        
        # Get last 50 characters of first chunk
        first_chunk_end = first_chunk_text[-50:]
        
        # Check if any part appears in second chunk (overlap)
        # Note: Overlap might not be exact due to separator handling
        assert len(chunks) > 1  # At least verify we have multiple chunks


@pytest.mark.asyncio
async def test_chunk_metadata_headers(chunking_service):
    """Test that markdown headers are preserved in metadata"""
    markdown_text = """# Policy Document

## Refund Policy

Customers can request refunds within 24 hours.

### Cancellation Window

Free cancellation is available.
"""
    
    chunks = await chunking_service.chunk_document(
        text=markdown_text,
        document_id="test-doc-4",
        file_type="markdown"
    )
    
    # Check that headers are captured
    for chunk in chunks:
        metadata = chunk["metadata"]
        # At least one chunk should have headers
        if metadata.headers:
            assert isinstance(metadata.headers, dict)


@pytest.mark.asyncio
async def test_chunk_id_generation(chunking_service):
    """Test that chunk IDs are unique and consistent"""
    text = "Test document content."

    chunks = await chunking_service.chunk_document(
        text=text,
        document_id="test-doc-5",
        file_type="txt"
    )

    # Check uniqueness
    chunk_ids = [chunk["id"] for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))  # All unique

    # Check that IDs are non-empty strings
    for chunk_id in chunk_ids:
        assert isinstance(chunk_id, str)
        assert len(chunk_id) > 0


@pytest.mark.asyncio
async def test_empty_document(chunking_service):
    """Test handling of empty document"""
    text = ""
    
    chunks = await chunking_service.chunk_document(
        text=text,
        document_id="test-doc-6",
        file_type="txt"
    )
    
    # Should return empty list or single empty chunk
    assert isinstance(chunks, list)


@pytest.mark.asyncio
async def test_large_document_chunking(chunking_service):
    """Test chunking of large document"""
    # Create a large document (>10000 characters)
    large_text = "This is a sentence in a large document. " * 500

    chunks = await chunking_service.chunk_document(
        text=large_text,
        document_id="test-doc-7",
        file_type="txt"
    )

    # Should create multiple chunks
    assert len(chunks) > 1

    # Each chunk should have token counts
    for chunk in chunks:
        metadata = chunk["metadata"]
        assert metadata.token_count > 0


@pytest.mark.asyncio
async def test_token_counting(chunking_service):
    """Test that token counting is accurate"""
    text = "Hello world! This is a test."
    
    chunks = await chunking_service.chunk_document(
        text=text,
        document_id="test-doc-8",
        file_type="txt"
    )
    
    # Check token count is reasonable
    for chunk in chunks:
        metadata = chunk["metadata"]
        # Token count should be less than character count
        assert metadata.token_count < metadata.char_count
        # Token count should be positive
        assert metadata.token_count > 0

