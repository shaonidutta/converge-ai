"""
Document management service for upload, processing, and management
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from fastapi import UploadFile

from src.rag.parsers import PDFParser, DOCXParser, TXTParser, MarkdownParser
from src.rag.chunking import ChunkingService
from src.rag.vector_store.pinecone_service import PineconeService
from src.rag.embeddings.embedding_service import EmbeddingService
from src.core.config.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Service for document upload, processing, and management"""
    
    def __init__(self):
        # Initialize parsers
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".doc": DOCXParser(),
            ".txt": TXTParser(),
            ".md": MarkdownParser(),
            ".markdown": MarkdownParser(),
        }
        
        # Initialize services
        self.chunking_service = ChunkingService(
            chunk_size=512,  # tokens
            chunk_overlap=50  # tokens
        )
        self.pinecone_service = PineconeService()
        self.embedding_service = EmbeddingService()
        
        # Upload directory
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_parser(self, file_extension: str):
        """Get appropriate parser for file type"""
        parser = self.parsers.get(file_extension.lower())
        if not parser:
            raise ValueError(f"Unsupported file type: {file_extension}")
        return parser
    
    async def upload_and_process_document(
        self,
        file: UploadFile,
        category: str,
        user_id: int,
        namespace: str = "policies"
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            file: Uploaded file
            category: Document category (policy, terms, refund, etc.)
            user_id: ID of user uploading document
            namespace: Pinecone namespace
            
        Returns:
            Processing result with document ID and chunk count
        """
        temp_file_path = None
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Save file temporarily
            file_extension = Path(file.filename).suffix
            temp_file_path = self.upload_dir / f"{document_id}{file_extension}"
            
            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"Saved uploaded file: {temp_file_path}")
            
            # Parse document
            parser = self._get_parser(file_extension)
            parsed_data = await parser.parse(temp_file_path)
            
            text = parsed_data["text"]
            file_metadata = parsed_data["metadata"]
            
            logger.info(f"Parsed document: {file.filename}, {len(text)} characters")
            
            # Chunk document
            chunks = await self.chunking_service.chunk_document(
                text=text,
                document_id=document_id,
                file_type=file_metadata["file_type"]
            )
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Prepare documents for Pinecone
            documents = []
            for chunk in chunks:
                chunk_metadata = chunk["metadata"]
                
                doc = {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "document_id": document_id,
                    "document_name": file.filename,
                    "document_title": file_metadata.get("title", file.filename),
                    "category": category,
                    "file_type": file_metadata["file_type"],
                    "section_title": chunk_metadata.section_title,
                    "chunk_index": chunk_metadata.chunk_index,
                    "total_chunks": chunk_metadata.total_chunks,
                    "token_count": chunk_metadata.token_count,
                    "char_count": chunk_metadata.char_count,
                    "uploaded_by_user_id": user_id,
                    "upload_date": datetime.utcnow().isoformat(),
                    "version": "1.0",
                }
                
                # Add hierarchical headers
                if chunk_metadata.headers:
                    doc.update({
                        f"header_{k}": v 
                        for k, v in chunk_metadata.headers.items()
                    })
                
                documents.append(doc)
            
            # Upload to Pinecone
            result = self.pinecone_service.upsert_documents(
                documents=documents,
                namespace=namespace,
                id_field="id",
                text_field="text"
            )
            
            logger.info(f"Uploaded {result['upserted_count']} chunks to Pinecone")
            
            # Clean up temporary file
            if temp_file_path and temp_file_path.exists():
                temp_file_path.unlink()
            
            return {
                "success": True,
                "document_id": document_id,
                "document_name": file.filename,
                "category": category,
                "chunks_created": len(chunks),
                "chunks_uploaded": result["upserted_count"],
                "namespace": namespace,
            }
        
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {e}")
            # Clean up on error
            if temp_file_path and temp_file_path.exists():
                temp_file_path.unlink()
            raise
    
    async def list_documents(
        self,
        namespace: str = "policies",
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all documents in namespace
        
        Args:
            namespace: Pinecone namespace
            category: Filter by category (optional)
            
        Returns:
            List of unique documents with metadata
        """
        # Query Pinecone to get all vectors (with metadata filter if category specified)
        filter_dict = {"category": category} if category else None
        
        # Get sample vectors to extract document list
        results = self.pinecone_service.query_by_text(
            query_text="policy document",  # Generic query to get samples
            top_k=1000,  # Get many results
            namespace=namespace,
            filter=filter_dict
        )
        
        # Extract unique documents
        documents_map = {}
        for result in results:
            doc_id = result["metadata"].get("document_id")
            if doc_id and doc_id not in documents_map:
                documents_map[doc_id] = {
                    "document_id": doc_id,
                    "document_name": result["metadata"].get("document_name"),
                    "document_title": result["metadata"].get("document_title"),
                    "category": result["metadata"].get("category"),
                    "file_type": result["metadata"].get("file_type"),
                    "total_chunks": result["metadata"].get("total_chunks"),
                    "upload_date": result["metadata"].get("upload_date"),
                    "uploaded_by_user_id": result["metadata"].get("uploaded_by_user_id"),
                }
        
        return list(documents_map.values())
    
    async def delete_document(
        self,
        document_id: str,
        namespace: str = "policies"
    ) -> Dict[str, Any]:
        """
        Delete all chunks of a document from Pinecone
        
        Args:
            document_id: Document ID to delete
            namespace: Pinecone namespace
            
        Returns:
            Deletion result
        """
        try:
            # Delete by metadata filter
            self.pinecone_service.index.delete(
                filter={"document_id": document_id},
                namespace=namespace
            )
            
            logger.info(f"Deleted document {document_id} from namespace {namespace}")
            
            return {
                "success": True,
                "document_id": document_id,
                "message": "Document deleted successfully"
            }
        
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        namespace: str = "policies",
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents by query
        
        Args:
            query: Search query
            top_k: Number of results
            namespace: Pinecone namespace
            category: Filter by category (optional)
            
        Returns:
            List of matching chunks with metadata
        """
        filter_dict = {"category": category} if category else None
        
        results = self.pinecone_service.query_by_text(
            query_text=query,
            top_k=top_k,
            namespace=namespace,
            filter=filter_dict
        )
        
        return results

