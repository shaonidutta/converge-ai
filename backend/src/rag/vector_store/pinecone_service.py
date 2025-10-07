"""
Pinecone Vector Store Service
Manages vector storage and retrieval using Pinecone serverless index
"""

from typing import List, Dict, Optional, Any, Tuple
import logging
from pinecone import Pinecone, ServerlessSpec
from functools import lru_cache
import time

from src.core.config.settings import settings
from src.rag.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Service for managing Pinecone vector database operations
    
    Configured for serverless deployment with:
    - Region: us-east-1
    - Cloud: AWS
    - Dimension: 384 (for all-MiniLM-L6-v2)
    - Metric: cosine
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        metric: Optional[str] = None,
        cloud: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize Pinecone service
        
        Args:
            api_key: Pinecone API key (default: from settings)
            index_name: Name of the Pinecone index (default: from settings)
            dimension: Embedding dimension (default: from settings)
            metric: Distance metric (default: from settings)
            cloud: Cloud provider (default: from settings)
            region: Cloud region (default: from settings)
        """
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self.dimension = dimension or settings.PINECONE_DIMENSION
        self.metric = metric or settings.PINECONE_METRIC
        self.cloud = cloud or settings.PINECONE_CLOUD
        self.region = region or settings.PINECONE_REGION
        
        # Initialize Pinecone client
        logger.info(f"Initializing Pinecone client for index: {self.index_name}")
        self.pc = Pinecone(api_key=self.api_key)
        
        # Get or create index
        self._ensure_index_exists()
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
        logger.info(f"Connected to Pinecone index: {self.index_name}")
        
        # Get embedding service
        self.embedding_service = get_embedding_service()
    
    def _ensure_index_exists(self):
        """
        Ensure the Pinecone index exists, create if it doesn't
        """
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                logger.info(f"Index '{self.index_name}' already exists")
                return
            
            # Create new serverless index
            logger.info(f"Creating new Pinecone serverless index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region
                )
            )
            
            # Wait for index to be ready
            logger.info("Waiting for index to be ready...")
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            logger.info(f"Index '{self.index_name}' created successfully")
            
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
    
    def upsert_vectors(
        self,
        vectors: List[Tuple[str, List[float], Dict[str, Any]]],
        namespace: str = ""
    ) -> Dict[str, int]:
        """
        Upsert vectors to Pinecone index
        
        Args:
            vectors: List of tuples (id, vector, metadata)
            namespace: Namespace for the vectors (default: "")
            
        Returns:
            Dictionary with upsert statistics
        """
        try:
            logger.info(f"Upserting {len(vectors)} vectors to namespace: {namespace or 'default'}")
            
            # Upsert vectors
            response = self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            logger.info(f"Successfully upserted {response.upserted_count} vectors")
            return {"upserted_count": response.upserted_count}
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise
    
    def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        namespace: str = "",
        id_field: str = "id",
        text_field: str = "text"
    ) -> Dict[str, int]:
        """
        Upsert documents with automatic embedding generation
        
        Args:
            documents: List of document dictionaries
            namespace: Namespace for the documents
            id_field: Field name for document ID
            text_field: Field name for document text
            
        Returns:
            Dictionary with upsert statistics
        """
        try:
            # Extract texts and generate embeddings
            texts = [doc[text_field] for doc in documents]
            embeddings = self.embedding_service.embed_documents(texts)
            
            # Prepare vectors for upsert
            vectors = []
            for doc, embedding in zip(documents, embeddings):
                doc_id = doc[id_field]
                
                # Prepare metadata (exclude text to save space, keep other fields)
                metadata = {k: v for k, v in doc.items() if k != text_field}
                metadata["text_preview"] = doc[text_field][:200]  # Store preview only
                
                vectors.append((doc_id, embedding, metadata))
            
            # Upsert to Pinecone
            return self.upsert_vectors(vectors, namespace)
            
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            raise
    
    def query(
        self,
        query_vector: List[float],
        top_k: int = 10,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone index with a vector
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Include metadata in results
            include_values: Include vector values in results
            
        Returns:
            List of matching results with scores
        """
        try:
            logger.debug(f"Querying index with top_k={top_k}, namespace={namespace or 'default'}")
            
            # Query Pinecone
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata,
                include_values=include_values
            )
            
            # Format results
            matches = []
            for match in results.matches:
                result = {
                    "id": match.id,
                    "score": match.score
                }
                if include_metadata and match.metadata:
                    result["metadata"] = match.metadata
                if include_values and match.values:
                    result["values"] = match.values
                
                matches.append(result)
            
            logger.debug(f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error querying index: {e}")
            raise
    
    def query_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone index with text (automatic embedding generation)
        
        Args:
            query_text: Query text
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Include metadata in results
            
        Returns:
            List of matching results with scores
        """
        try:
            # Generate query embedding
            query_vector = self.embedding_service.embed_query(query_text)
            
            # Query with vector
            return self.query(
                query_vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata
            )
            
        except Exception as e:
            logger.error(f"Error querying by text: {e}")
            raise
    
    def delete(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete vectors from index
        
        Args:
            ids: List of vector IDs to delete
            delete_all: Delete all vectors in namespace
            namespace: Namespace to delete from
            filter: Metadata filter for deletion
            
        Returns:
            Deletion response
        """
        try:
            if delete_all:
                logger.warning(f"Deleting all vectors from namespace: {namespace or 'default'}")
                response = self.index.delete(delete_all=True, namespace=namespace)
            elif ids:
                logger.info(f"Deleting {len(ids)} vectors from namespace: {namespace or 'default'}")
                response = self.index.delete(ids=ids, namespace=namespace)
            elif filter:
                logger.info(f"Deleting vectors matching filter from namespace: {namespace or 'default'}")
                response = self.index.delete(filter=filter, namespace=namespace)
            else:
                raise ValueError("Must provide either ids, delete_all=True, or filter")
            
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise
    
    def get_index_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get statistics about the index
        
        Args:
            namespace: Namespace to get stats for (empty for all)
            
        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if Pinecone service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to get index stats
            self.get_index_stats()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


@lru_cache()
def get_pinecone_service() -> PineconeService:
    """
    Get cached Pinecone service instance (singleton pattern)
    
    Returns:
        PineconeService instance
    """
    return PineconeService()


# Export for easy imports
__all__ = ["PineconeService", "get_pinecone_service"]

