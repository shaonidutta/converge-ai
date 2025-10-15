"""
Diagnostic script to analyze RAG scores and identify improvement areas

This script:
1. Tests various queries with detailed score analysis
2. Examines embedding quality
3. Analyzes chunk relevance
4. Identifies improvement opportunities
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.rag.vector_store.pinecone_service import PineconeService
from src.rag.embeddings.embedding_service import EmbeddingService


async def analyze_query_results(query: str, pinecone_service: PineconeService):
    """Analyze search results for a query"""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    # Search with different top_k values
    for top_k in [3, 5, 10]:
        print(f"\n--- Top {top_k} Results ---")
        results = pinecone_service.query_by_text(
            query_text=query,
            top_k=top_k,
            namespace="policies",
            include_metadata=True
        )
        
        for idx, result in enumerate(results, 1):
            score = result.get("score", 0.0)
            metadata = result.get("metadata", {})
            text_preview = metadata.get("text_preview", "")[:150]
            policy_type = metadata.get("policy_type", "Unknown")
            section = metadata.get("section", "Unknown")
            
            print(f"\n  Result {idx}:")
            print(f"    Score: {score:.4f}")
            print(f"    Policy: {policy_type}")
            print(f"    Section: {section}")
            print(f"    Preview: {text_preview}...")
            
            # Score analysis
            if score >= 0.8:
                quality = "EXCELLENT"
            elif score >= 0.7:
                quality = "GOOD"
            elif score >= 0.6:
                quality = "FAIR"
            elif score >= 0.5:
                quality = "POOR"
            else:
                quality = "VERY POOR"
            
            print(f"    Quality: {quality}")


async def test_embedding_quality(embedding_service: EmbeddingService):
    """Test embedding quality with similar queries"""
    print(f"\n{'='*80}")
    print("EMBEDDING QUALITY TEST")
    print(f"{'='*80}")
    
    # Test similar queries
    queries = [
        "What is your cancellation policy?",
        "How do I cancel my booking?",
        "Can I cancel my service?",
        "Tell me about cancellations",
    ]
    
    print("\nGenerating embeddings for similar queries...")
    embeddings = embedding_service.embed_texts(queries)
    
    # Calculate cosine similarity between queries
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    print("\nCosine Similarity Matrix:")
    print("(Higher = more similar, should be high for similar queries)")
    print("\n" + " " * 40, end="")
    for i in range(len(queries)):
        print(f"Q{i+1:2d}", end="  ")
    print()
    
    for i, query_i in enumerate(queries):
        print(f"Q{i+1}: {query_i[:35]:35s}", end=" ")
        for j, query_j in enumerate(queries):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            print(f"{sim:.2f}", end="  ")
        print()
    
    print("\nExpected: Similar queries should have similarity > 0.8")


async def analyze_chunk_distribution(pinecone_service: PineconeService):
    """Analyze how chunks are distributed"""
    print(f"\n{'='*80}")
    print("CHUNK DISTRIBUTION ANALYSIS")
    print(f"{'='*80}")
    
    # Get index stats
    try:
        stats = pinecone_service.index.describe_index_stats()
        print(f"\nIndex Statistics:")
        print(f"  Total Vectors: {stats.get('total_vector_count', 'N/A')}")
        print(f"  Dimension: {stats.get('dimension', 'N/A')}")
        
        namespaces = stats.get('namespaces', {})
        for ns_name, ns_stats in namespaces.items():
            print(f"\n  Namespace: {ns_name}")
            print(f"    Vector Count: {ns_stats.get('vector_count', 'N/A')}")
    except Exception as e:
        print(f"  Error getting stats: {e}")


async def test_query_preprocessing():
    """Test different query preprocessing strategies"""
    print(f"\n{'='*80}")
    print("QUERY PREPROCESSING TEST")
    print(f"{'='*80}")
    
    original_query = "What is your cancellation policy? Can I get a refund if I cancel 2 hours before?"
    
    print(f"\nOriginal Query:")
    print(f"  {original_query}")
    
    # Strategy 1: Split into multiple queries
    print(f"\nStrategy 1: Split into sub-queries")
    sub_queries = [
        "What is your cancellation policy?",
        "Can I get a refund if I cancel 2 hours before?"
    ]
    for i, sq in enumerate(sub_queries, 1):
        print(f"  Sub-query {i}: {sq}")
    
    # Strategy 2: Extract key terms
    print(f"\nStrategy 2: Key terms extraction")
    key_terms = ["cancellation policy", "refund", "cancel 2 hours before"]
    for term in key_terms:
        print(f"  - {term}")
    
    # Strategy 3: Query expansion
    print(f"\nStrategy 3: Query expansion")
    expanded = [
        original_query,
        "cancellation refund policy timeframe",
        "booking cancellation 2 hours refund eligibility"
    ]
    for i, exp in enumerate(expanded, 1):
        print(f"  Expansion {i}: {exp}")


async def test_reranking_strategy(pinecone_service: PineconeService):
    """Test if reranking improves results"""
    print(f"\n{'='*80}")
    print("RERANKING STRATEGY TEST")
    print(f"{'='*80}")
    
    query = "What is your cancellation policy? Can I get a refund if I cancel 2 hours before?"
    
    # Get initial results
    results = pinecone_service.query_by_text(
        query_text=query,
        top_k=10,
        namespace="policies",
        include_metadata=True
    )
    
    print(f"\nInitial Top 10 Results (by vector similarity):")
    for idx, result in enumerate(results, 1):
        score = result.get("score", 0.0)
        metadata = result.get("metadata", {})
        policy_type = metadata.get("policy_type", "Unknown")
        section = metadata.get("section", "Unknown")
        print(f"  {idx}. Score: {score:.4f} | {policy_type} / {section}")
    
    # Simulate keyword-based reranking
    print(f"\nSimulated Reranking (keyword boost):")
    keywords = ["cancellation", "refund", "2 hours", "cancel"]
    
    reranked = []
    for result in results:
        metadata = result.get("metadata", {})
        text_preview = metadata.get("text_preview", "").lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw in text_preview)
        
        # Boost score based on keyword matches
        original_score = result.get("score", 0.0)
        boosted_score = original_score + (keyword_matches * 0.05)
        
        reranked.append({
            **result,
            "boosted_score": boosted_score,
            "keyword_matches": keyword_matches
        })
    
    # Sort by boosted score
    reranked.sort(key=lambda x: x["boosted_score"], reverse=True)
    
    for idx, result in enumerate(reranked[:10], 1):
        original_score = result.get("score", 0.0)
        boosted_score = result.get("boosted_score", 0.0)
        keyword_matches = result.get("keyword_matches", 0)
        metadata = result.get("metadata", {})
        policy_type = metadata.get("policy_type", "Unknown")
        section = metadata.get("section", "Unknown")
        
        change = "↑" if boosted_score > original_score else "="
        print(f"  {idx}. Score: {original_score:.4f} → {boosted_score:.4f} {change} | Keywords: {keyword_matches} | {policy_type} / {section}")


async def main():
    """Main diagnostic function"""
    print("="*80)
    print("RAG SCORE DIAGNOSTIC TOOL")
    print("="*80)
    
    # Initialize services
    print("\n1. Initializing services...")
    try:
        pinecone_service = PineconeService()
        embedding_service = EmbeddingService()
        print("   ✅ Services initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test queries
    test_queries = [
        "What is your cancellation policy? Can I get a refund if I cancel 2 hours before?",
        "When can I get a full refund for my booking?",
        "How long does it take to process a refund?",
    ]
    
    # Run diagnostics
    print("\n2. Analyzing query results...")
    for query in test_queries:
        await analyze_query_results(query, pinecone_service)
    
    print("\n3. Testing embedding quality...")
    await test_embedding_quality(embedding_service)
    
    print("\n4. Analyzing chunk distribution...")
    await analyze_chunk_distribution(pinecone_service)
    
    print("\n5. Testing query preprocessing strategies...")
    await test_query_preprocessing()
    
    print("\n6. Testing reranking strategy...")
    await test_reranking_strategy(pinecone_service)
    
    # Recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS FOR IMPROVEMENT")
    print(f"{'='*80}")
    
    print("\n1. Query Preprocessing:")
    print("   - Split complex queries into sub-queries")
    print("   - Extract and emphasize key terms")
    print("   - Use query expansion for better coverage")
    
    print("\n2. Reranking:")
    print("   - Implement keyword-based reranking")
    print("   - Boost scores for exact keyword matches")
    print("   - Consider semantic reranking with cross-encoder")
    
    print("\n3. Chunking Strategy:")
    print("   - Increase chunk size to 800-1000 characters")
    print("   - Increase overlap to 100-150 characters")
    print("   - Ensure chunks contain complete semantic units")
    
    print("\n4. Embedding Model:")
    print("   - Consider fine-tuning on policy-specific data")
    print("   - Try larger models (e.g., all-mpnet-base-v2)")
    print("   - Experiment with domain-specific models")
    
    print("\n5. Grounding Score:")
    print("   - Adjust keyword overlap weight")
    print("   - Add semantic similarity check")
    print("   - Consider LLM-based grounding evaluation")
    
    print("\n✅ Diagnostic complete!")


if __name__ == "__main__":
    asyncio.run(main())

