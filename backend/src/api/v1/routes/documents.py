"""
Document management API endpoints
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from pydantic import BaseModel

from src.services.document_service import DocumentService
from src.api.dependencies.auth import get_current_user
from src.models.user import User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


# Response models
class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    document_id: str
    document_name: str
    category: str
    chunks_created: int
    chunks_uploaded: int
    namespace: str


class DocumentListItem(BaseModel):
    """Document list item"""
    document_id: str
    document_name: str
    document_title: str
    category: str
    file_type: str
    total_chunks: int
    upload_date: str
    uploaded_by_user_id: int


class DocumentDeleteResponse(BaseModel):
    """Response for document deletion"""
    success: bool
    document_id: str
    message: str


class DocumentSearchResult(BaseModel):
    """Document search result"""
    chunk_id: str
    text: str
    score: float
    metadata: dict


# Initialize service
document_service = DocumentService()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    category: str = Form(..., description="Document category (policy, terms, refund, etc.)"),
    namespace: str = Form(default="policies", description="Pinecone namespace"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a document
    
    - **file**: Document file (PDF, DOCX, TXT, MD)
    - **category**: Document category
    - **namespace**: Pinecone namespace (default: policies)
    
    Returns document ID and processing statistics
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".doc", ".txt", ".md", ".markdown"]
    file_extension = f".{file.filename.split('.')[-1].lower()}"
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )
    
    try:
        result = await document_service.upload_and_process_document(
            file=file,
            category=category,
            user_id=current_user.id,
            namespace=namespace
        )
        
        return DocumentUploadResponse(**result)
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    namespace: str = "policies",
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    List all documents in namespace
    
    - **namespace**: Pinecone namespace (default: policies)
    - **category**: Filter by category (optional)
    
    Returns list of documents with metadata
    """
    try:
        documents = await document_service.list_documents(
            namespace=namespace,
            category=category
        )
        
        return [DocumentListItem(**doc) for doc in documents]
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    namespace: str = "policies",
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document and all its chunks
    
    - **document_id**: Document ID to delete
    - **namespace**: Pinecone namespace (default: policies)
    
    Returns deletion confirmation
    """
    try:
        result = await document_service.delete_document(
            document_id=document_id,
            namespace=namespace
        )
        
        return DocumentDeleteResponse(**result)
    
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/search", response_model=List[DocumentSearchResult])
async def search_documents(
    query: str,
    top_k: int = 5,
    namespace: str = "policies",
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Search documents by query
    
    - **query**: Search query
    - **top_k**: Number of results (default: 5)
    - **namespace**: Pinecone namespace (default: policies)
    - **category**: Filter by category (optional)
    
    Returns matching document chunks
    """
    try:
        results = await document_service.search_documents(
            query=query,
            top_k=top_k,
            namespace=namespace,
            category=category
        )
        
        return [
            DocumentSearchResult(
                chunk_id=r["id"],
                text=r["text"],
                score=r["score"],
                metadata=r["metadata"]
            )
            for r in results
        ]
    
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search documents: {str(e)}"
        )

