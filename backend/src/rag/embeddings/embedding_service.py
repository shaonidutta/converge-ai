"""
Embedding Service using Sentence Transformers
Provides text embedding generation using sentence-transformers/all-MiniLM-L6-v2
"""

from typing import List, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import logging

from src.core.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using Sentence Transformers
    
    Uses sentence-transformers/all-MiniLM-L6-v2 model which produces 384-dimensional embeddings
    Optimized for semantic similarity tasks with good balance of speed and quality
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        normalize_embeddings: Optional[bool] = None,
        batch_size: Optional[int] = None
    ):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the sentence-transformers model (default: from settings)
            device: Device to run model on ('cpu', 'cuda', 'mps') (default: from settings)
            normalize_embeddings: Whether to normalize embeddings (default: from settings)
            batch_size: Batch size for encoding (default: from settings)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.normalize_embeddings = normalize_embeddings if normalize_embeddings is not None else settings.EMBEDDING_NORMALIZE
        self.batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        self.embedding_dimension = settings.EMBEDDING_DIMENSION
        
        # Load the model
        logger.info(f"Loading embedding model: {self.model_name} on device: {self.device}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        # Verify embedding dimension
        actual_dim = self.model.get_sentence_embedding_dimension()
        if actual_dim != self.embedding_dimension:
            logger.warning(
                f"Model embedding dimension ({actual_dim}) does not match configured dimension ({self.embedding_dimension}). "
                f"Using model dimension: {actual_dim}"
            )
            self.embedding_dimension = actual_dim
        
        logger.info(f"Embedding model loaded successfully. Dimension: {self.embedding_dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Encode single text
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.normalize_embeddings,
                convert_to_numpy=True
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Encode batch of texts
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100  # Show progress for large batches
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings for {len(texts)} texts: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        For all-MiniLM-L6-v2, queries and documents use the same encoding
        This method is provided for API consistency with other embedding models
        
        Args:
            query: Search query text
            
        Returns:
            List of floats representing the query embedding
        """
        return self.embed_text(query)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for documents
        
        For all-MiniLM-L6-v2, queries and documents use the same encoding
        This method is provided for API consistency with other embedding models
        
        Args:
            documents: List of document texts
            
        Returns:
            List of embedding vectors
        """
        return self.embed_texts(documents)
    
    def similarity(
        self, 
        embedding1: Union[List[float], np.ndarray], 
        embedding2: Union[List[float], np.ndarray]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            # Convert to numpy arrays if needed
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # Calculate cosine similarity
            # If embeddings are normalized, this is just dot product
            if self.normalize_embeddings:
                similarity = np.dot(embedding1, embedding2)
            else:
                # Manual cosine similarity calculation
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise
    
    def batch_similarity(
        self,
        query_embedding: Union[List[float], np.ndarray],
        document_embeddings: List[Union[List[float], np.ndarray]]
    ) -> List[float]:
        """
        Calculate similarity between a query and multiple documents
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of document embedding vectors
            
        Returns:
            List of similarity scores
        """
        try:
            # Convert to numpy arrays
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding)
            
            doc_array = np.array([
                emb if isinstance(emb, np.ndarray) else np.array(emb)
                for emb in document_embeddings
            ])
            
            # Calculate similarities
            if self.normalize_embeddings:
                # Simple dot product for normalized embeddings
                similarities = np.dot(doc_array, query_embedding)
            else:
                # Manual cosine similarity
                query_norm = np.linalg.norm(query_embedding)
                doc_norms = np.linalg.norm(doc_array, axis=1)
                similarities = np.dot(doc_array, query_embedding) / (doc_norms * query_norm)
            
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Error calculating batch similarities: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model
        
        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return self.embedding_dimension
    
    def get_model_info(self) -> dict:
        """
        Get information about the embedding model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "device": self.device,
            "normalize_embeddings": self.normalize_embeddings,
            "batch_size": self.batch_size,
            "max_seq_length": self.model.max_seq_length
        }


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """
    Get cached embedding service instance (singleton pattern)
    
    Returns:
        EmbeddingService instance
    """
    return EmbeddingService()


# Export for easy imports
__all__ = ["EmbeddingService", "get_embedding_service"]

