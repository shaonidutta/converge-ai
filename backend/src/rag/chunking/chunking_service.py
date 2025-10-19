"""
Hybrid chunking service combining semantic (markdown header) and token-based splitting
Uses RecursiveCharacterTextSplitter for better quality chunking
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
import tiktoken


logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk"""
    chunk_id: str
    chunk_index: int
    total_chunks: int
    section_title: Optional[str]
    headers: Dict[str, str]  # Hierarchical headers (H1, H2, H3)
    token_count: int
    char_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ChunkingService:
    """
    Hybrid chunking service that combines:
    1. Semantic chunking (markdown headers) for structured documents
    2. Recursive character-based chunking for optimal token usage
    """
    
    def __init__(
        self,
        chunk_size: int = 512,  # tokens
        chunk_overlap: int = 50,  # tokens
        encoding_name: str = "cl100k_base"  # GPT-4 encoding
    ):
        """
        Initialize chunking service
        
        Args:
            chunk_size: Maximum chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            encoding_name: Tiktoken encoding name
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize tiktoken encoder for accurate token counting
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding {encoding_name}: {e}")
            self.encoding = None
        
        # Markdown header splitter (semantic chunking)
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ],
            strip_headers=False  # Keep headers in chunks for context
        )
        
        # Recursive character text splitter (better than simple character splitting)
        # Uses hierarchical separators: paragraphs -> sentences -> words
        self.token_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 4,  # Approximate: 1 token ≈ 4 chars
            chunk_overlap=chunk_overlap * 4,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
            keep_separator=True
        )
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: approximate 1 token ≈ 4 characters
            return len(text) // 4
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """
        Generate unique chunk ID
        
        Args:
            document_id: Document identifier
            chunk_index: Index of chunk
            
        Returns:
            Unique chunk ID
        """
        return hashlib.md5(f"{document_id}_{chunk_index}".encode()).hexdigest()
    
    async def chunk_document(
        self,
        text: str,
        document_id: str,
        file_type: str = "markdown"
    ) -> List[Dict[str, Any]]:
        """
        Chunk document using hybrid strategy
        
        Args:
            text: Document text
            document_id: Unique document identifier
            file_type: Type of document (markdown, pdf, docx, txt)
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Step 1: Split by markdown headers (semantic chunking) for markdown files
        if file_type in ["markdown", "md"]:
            try:
                header_chunks = self.header_splitter.split_text(text)
                logger.info(f"Markdown header splitting created {len(header_chunks)} sections")
            except Exception as e:
                logger.warning(f"Markdown header splitting failed: {e}. Falling back to token-based.")
                header_chunks = [{"page_content": text, "metadata": {}}]
        else:
            # For non-markdown, treat as single section
            header_chunks = [{"page_content": text, "metadata": {}}]
        
        # Step 2: Further split large sections using RecursiveCharacterTextSplitter
        all_chunks = []
        for section in header_chunks:
            # Handle both dict and Document objects from langchain
            if isinstance(section, dict):
                section_text = section.get("page_content", section.get("content", str(section)))
                section_metadata = section.get("metadata", {})
            else:
                # LangChain Document object
                section_text = section.page_content if hasattr(section, 'page_content') else str(section)
                section_metadata = section.metadata if hasattr(section, 'metadata') else {}
            
            # Check if section exceeds token limit
            token_count = self._count_tokens(section_text)
            
            if token_count > self.chunk_size:
                # Split large section into smaller chunks using RecursiveCharacterTextSplitter
                sub_chunks = self.token_splitter.split_text(section_text)
                logger.info(f"Split large section ({token_count} tokens) into {len(sub_chunks)} chunks")
                for sub_chunk in sub_chunks:
                    all_chunks.append({
                        "text": sub_chunk,
                        "headers": section_metadata
                    })
            else:
                # Section is small enough, keep as is
                all_chunks.append({
                    "text": section_text,
                    "headers": section_metadata
                })
        
        # Step 3: Create chunk objects with metadata
        total_chunks = len(all_chunks)
        
        for idx, chunk_data in enumerate(all_chunks):
            chunk_text = chunk_data["text"]
            headers = chunk_data["headers"]
            
            # Generate chunk ID
            chunk_id = self._generate_chunk_id(document_id, idx)
            
            # Extract section title from headers
            section_title = (
                headers.get("h1") or 
                headers.get("h2") or 
                headers.get("h3") or 
                "General"
            )
            
            # Count tokens and characters
            token_count = self._count_tokens(chunk_text)
            char_count = len(chunk_text)
            
            # Create chunk metadata
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                chunk_index=idx,
                total_chunks=total_chunks,
                section_title=section_title,
                headers=headers,
                token_count=token_count,
                char_count=char_count
            )
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": metadata
            })
        
        logger.info(
            f"Chunked document {document_id}: "
            f"{total_chunks} chunks, "
            f"avg {sum(c['metadata'].token_count for c in chunks) / total_chunks:.0f} tokens/chunk"
        )
        
        return chunks
    
    async def chunk_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents in batch
        
        Args:
            documents: List of documents with 'text', 'document_id', 'file_type'
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            chunks = await self.chunk_document(
                text=doc["text"],
                document_id=doc["document_id"],
                file_type=doc.get("file_type", "markdown")
            )
            all_chunks.extend(chunks)
        
        return all_chunks

