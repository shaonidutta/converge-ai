"""
Script to upload policy documents to Pinecone vector database

This script:
1. Reads policy documents from backend/data/policies/
2. Chunks documents into smaller pieces with overlap
3. Generates embeddings for each chunk
4. Uploads to Pinecone with metadata
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.rag.vector_store.pinecone_service import PineconeService
from src.rag.embeddings.embedding_service import EmbeddingService


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Chunk text into smaller pieces with overlap

    IMPROVED: Larger chunks (800 chars) with more overlap (100 chars) for better context

    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters (default: 800)
        overlap: Number of characters to overlap between chunks (default: 100)

    Returns:
        List of text chunks
    """
    # Split by paragraphs first
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk size, save current chunk
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous chunk
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def extract_metadata_from_markdown(content: str, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from markdown document
    
    Args:
        content: Markdown content
        filename: Name of the file
        
    Returns:
        Dictionary with metadata
    """
    metadata = {
        "policy_type": filename.replace("_policy.md", "").replace("_", " ").title(),
        "filename": filename
    }
    
    # Extract version and last updated from content
    version_match = re.search(r'## Version: (.+)', content)
    if version_match:
        metadata["version"] = version_match.group(1).strip()
    
    updated_match = re.search(r'## Last Updated: (.+)', content)
    if updated_match:
        metadata["last_updated"] = updated_match.group(1).strip()
    
    return metadata


def extract_section_from_chunk(chunk: str) -> str:
    """
    Extract section name from chunk (first heading)
    
    Args:
        chunk: Text chunk
        
    Returns:
        Section name or "General"
    """
    # Look for markdown headings
    heading_match = re.search(r'^#+\s+(.+)$', chunk, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    return "General"


def process_policy_document(
    filepath: Path,
    pinecone_service: PineconeService,
    embedding_service: EmbeddingService,
    namespace: str = "policies"
) -> int:
    """
    Process a single policy document and upload to Pinecone
    
    Args:
        filepath: Path to the policy document
        pinecone_service: Pinecone service instance
        embedding_service: Embedding service instance
        namespace: Pinecone namespace
        
    Returns:
        Number of chunks uploaded
    """
    print(f"\nProcessing: {filepath.name}")
    
    # Read document
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract base metadata
    base_metadata = extract_metadata_from_markdown(content, filepath.name)
    print(f"  Policy Type: {base_metadata['policy_type']}")
    print(f"  Version: {base_metadata.get('version', 'N/A')}")
    
    # Chunk the document (IMPROVED: larger chunks with more overlap)
    chunks = chunk_text(content, chunk_size=800, overlap=100)
    print(f"  Created {len(chunks)} chunks (800 chars, 100 overlap)")
    
    # Prepare documents for upload
    documents = []
    for idx, chunk in enumerate(chunks):
        # Generate unique ID
        chunk_id = hashlib.md5(f"{filepath.name}_{idx}".encode()).hexdigest()
        
        # Extract section from chunk
        section = extract_section_from_chunk(chunk)
        
        # Prepare document
        doc = {
            "id": chunk_id,
            "text": chunk,
            "policy_type": base_metadata["policy_type"],
            "section": section,
            "filename": base_metadata["filename"],
            "version": base_metadata.get("version", "1.0"),
            "last_updated": base_metadata.get("last_updated", "2025-10-14"),
            "chunk_index": idx,
            "total_chunks": len(chunks)
        }
        documents.append(doc)
    
    # Upload to Pinecone
    print(f"  Uploading to Pinecone namespace: {namespace}")
    result = pinecone_service.upsert_documents(
        documents=documents,
        namespace=namespace,
        id_field="id",
        text_field="text"
    )
    
    print(f"  ✅ Uploaded {result['upserted_count']} chunks")
    return result['upserted_count']


def main():
    """Main function to process all policy documents"""
    print("=" * 60)
    print("Policy Documents Upload to Pinecone")
    print("=" * 60)
    
    # Initialize services
    print("\n1. Initializing services...")
    try:
        pinecone_service = PineconeService()
        embedding_service = EmbeddingService()
        print("   ✅ Services initialized")
    except Exception as e:
        print(f"   ❌ Error initializing services: {e}")
        return
    
    # Find policy documents
    policies_dir = backend_dir / "data" / "policies"
    if not policies_dir.exists():
        print(f"\n❌ Policies directory not found: {policies_dir}")
        return
    
    policy_files = list(policies_dir.glob("*.md"))
    if not policy_files:
        print(f"\n❌ No policy documents found in: {policies_dir}")
        return
    
    print(f"\n2. Found {len(policy_files)} policy documents")
    for f in policy_files:
        print(f"   - {f.name}")
    
    # Process each document
    print("\n3. Processing and uploading documents...")
    total_chunks = 0
    
    for filepath in policy_files:
        try:
            chunks_uploaded = process_policy_document(
                filepath=filepath,
                pinecone_service=pinecone_service,
                embedding_service=embedding_service,
                namespace="policies"
            )
            total_chunks += chunks_uploaded
        except Exception as e:
            print(f"   ❌ Error processing {filepath.name}: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("Upload Complete!")
    print("=" * 60)
    print(f"Total documents processed: {len(policy_files)}")
    print(f"Total chunks uploaded: {total_chunks}")
    print(f"Namespace: policies")
    print("\n✅ Policy documents are now searchable in Pinecone!")


if __name__ == "__main__":
    main()

