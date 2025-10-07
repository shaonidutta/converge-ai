"""
Test script for Embedding Service and Pinecone Vector Store
Tests the configuration and basic functionality
"""

import sys
import os
from pathlib import Path

# Add backend/src to path
backend_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_path))

import asyncio
from typing import List
import numpy as np

from rag.embeddings import get_embedding_service
from rag.vector_store import get_pinecone_service
from core.config.settings import settings


def test_configuration():
    """Test configuration settings"""
    print("\n" + "="*80)
    print("TESTING CONFIGURATION")
    print("="*80)
    
    print("\n📋 Pinecone Configuration:")
    print(f"  - Index Name: {settings.PINECONE_INDEX_NAME}")
    print(f"  - Dimension: {settings.PINECONE_DIMENSION}")
    print(f"  - Metric: {settings.PINECONE_METRIC}")
    print(f"  - Cloud: {settings.PINECONE_CLOUD}")
    print(f"  - Region: {settings.PINECONE_REGION}")
    print(f"  - Capacity Mode: {settings.PINECONE_CAPACITY_MODE}")
    
    print("\n🤖 Embedding Configuration:")
    print(f"  - Model: {settings.EMBEDDING_MODEL}")
    print(f"  - Dimension: {settings.EMBEDDING_DIMENSION}")
    print(f"  - Device: {settings.EMBEDDING_DEVICE}")
    print(f"  - Normalize: {settings.EMBEDDING_NORMALIZE}")
    print(f"  - Batch Size: {settings.EMBEDDING_BATCH_SIZE}")
    
    # Verify dimension match
    if settings.PINECONE_DIMENSION == settings.EMBEDDING_DIMENSION:
        print("\n✅ Pinecone and Embedding dimensions match!")
    else:
        print(f"\n❌ WARNING: Dimension mismatch! Pinecone: {settings.PINECONE_DIMENSION}, Embedding: {settings.EMBEDDING_DIMENSION}")
    
    return True


def test_embedding_service():
    """Test embedding service"""
    print("\n" + "="*80)
    print("TESTING EMBEDDING SERVICE")
    print("="*80)
    
    try:
        # Get embedding service
        print("\n📦 Loading embedding service...")
        embedding_service = get_embedding_service()
        
        # Get model info
        model_info = embedding_service.get_model_info()
        print("\n✅ Embedding service loaded successfully!")
        print(f"\n📊 Model Information:")
        for key, value in model_info.items():
            print(f"  - {key}: {value}")
        
        # Test single text embedding
        print("\n🔤 Testing single text embedding...")
        test_text = "This is a test sentence for embedding generation."
        embedding = embedding_service.embed_text(test_text)
        print(f"  - Input: '{test_text}'")
        print(f"  - Embedding dimension: {len(embedding)}")
        print(f"  - First 5 values: {embedding[:5]}")
        
        # Test batch embedding
        print("\n📚 Testing batch text embedding...")
        test_texts = [
            "The weather is lovely today.",
            "It's so sunny outside!",
            "He drove to the stadium.",
            "Python is a programming language.",
            "Machine learning is fascinating."
        ]
        embeddings = embedding_service.embed_texts(test_texts)
        print(f"  - Number of texts: {len(test_texts)}")
        print(f"  - Number of embeddings: {len(embeddings)}")
        print(f"  - Embedding dimension: {len(embeddings[0])}")
        
        # Test similarity calculation
        print("\n🔍 Testing similarity calculation...")
        emb1 = embeddings[0]  # "The weather is lovely today."
        emb2 = embeddings[1]  # "It's so sunny outside!"
        emb3 = embeddings[3]  # "Python is a programming language."
        
        sim_weather = embedding_service.similarity(emb1, emb2)
        sim_unrelated = embedding_service.similarity(emb1, emb3)
        
        print(f"  - Similarity (weather sentences): {sim_weather:.4f}")
        print(f"  - Similarity (unrelated sentences): {sim_unrelated:.4f}")
        
        if sim_weather > sim_unrelated:
            print("  ✅ Similarity scores make sense!")
        else:
            print("  ⚠️  Unexpected similarity scores")
        
        # Test batch similarity
        print("\n📊 Testing batch similarity...")
        query_emb = embeddings[0]
        doc_embs = embeddings[1:]
        similarities = embedding_service.batch_similarity(query_emb, doc_embs)
        print(f"  - Query: '{test_texts[0]}'")
        print(f"  - Similarities with other texts:")
        for i, (text, sim) in enumerate(zip(test_texts[1:], similarities), 1):
            print(f"    {i}. {sim:.4f} - '{text}'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing embedding service: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pinecone_service():
    """Test Pinecone service"""
    print("\n" + "="*80)
    print("TESTING PINECONE SERVICE")
    print("="*80)
    
    try:
        # Get Pinecone service
        print("\n📦 Initializing Pinecone service...")
        pinecone_service = get_pinecone_service()
        print("✅ Pinecone service initialized successfully!")
        
        # Health check
        print("\n🏥 Running health check...")
        is_healthy = pinecone_service.health_check()
        if is_healthy:
            print("✅ Pinecone service is healthy!")
        else:
            print("❌ Pinecone service health check failed!")
            return False
        
        # Get index stats
        print("\n📊 Getting index statistics...")
        stats = pinecone_service.get_index_stats()
        print(f"  - Total vectors: {stats['total_vector_count']}")
        print(f"  - Dimension: {stats['dimension']}")
        print(f"  - Index fullness: {stats['index_fullness']}")
        print(f"  - Namespaces: {stats['namespaces']}")
        
        # Test document upsert
        print("\n📝 Testing document upsert...")
        test_documents = [
            {
                "id": "test-doc-1",
                "text": "Pinecone is a vector database for machine learning applications.",
                "category": "technology",
                "source": "test"
            },
            {
                "id": "test-doc-2",
                "text": "Sentence transformers generate high-quality embeddings for semantic search.",
                "category": "technology",
                "source": "test"
            },
            {
                "id": "test-doc-3",
                "text": "The weather is beautiful today with clear blue skies.",
                "category": "weather",
                "source": "test"
            }
        ]
        
        result = pinecone_service.upsert_documents(
            documents=test_documents,
            namespace="test"
        )
        print(f"  ✅ Upserted {result['upserted_count']} documents")
        
        # Test text query
        print("\n🔍 Testing text query...")
        query_text = "What is a vector database?"
        results = pinecone_service.query_by_text(
            query_text=query_text,
            top_k=3,
            namespace="test"
        )
        
        print(f"  - Query: '{query_text}'")
        print(f"  - Results:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. Score: {result['score']:.4f}")
            print(f"       ID: {result['id']}")
            if 'metadata' in result:
                print(f"       Category: {result['metadata'].get('category', 'N/A')}")
                print(f"       Preview: {result['metadata'].get('text_preview', 'N/A')[:80]}...")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        pinecone_service.delete(
            ids=["test-doc-1", "test-doc-2", "test-doc-3"],
            namespace="test"
        )
        print("  ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Pinecone service: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("EMBEDDING & PINECONE INTEGRATION TEST")
    print("="*80)
    print("\nTesting configuration for:")
    print("  - Model: sentence-transformers/all-MiniLM-L6-v2")
    print("  - Dimension: 384")
    print("  - Pinecone: Serverless (us-east-1, AWS)")
    
    results = {
        "Configuration": False,
        "Embedding Service": False,
        "Pinecone Service": False
    }
    
    # Run tests
    results["Configuration"] = test_configuration()
    results["Embedding Service"] = test_embedding_service()
    results["Pinecone Service"] = test_pinecone_service()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

