#!/usr/bin/env python3
"""
ConvergeAI Backend - Project Structure Setup Script

This script creates the complete directory structure for the backend
with all necessary __init__.py files.
"""

import os
from pathlib import Path


def create_directory_structure():
    """Create the complete backend directory structure."""
    
    # Get the backend root directory
    backend_root = Path(__file__).parent.parent
    
    # Define the directory structure
    directories = [
        # Source directories
        "src",
        "src/config",
        "src/models",
        "src/schemas",
        "src/repositories",
        "src/services",
        "src/middleware",
        "src/utils",
        
        # API directories
        "src/api",
        "src/api/v1",
        "src/api/v1/endpoints",
        "src/api/v1/dependencies",
        "src/api/middleware",
        
        # Core directories
        "src/core",
        "src/core/database",
        "src/core/cache",
        "src/core/security",
        "src/core/models",
        "src/core/repositories",
        "src/core/services",
        
        # Agent directories
        "src/agents",
        "src/agents/base",
        "src/agents/coordinator",
        "src/agents/booking",
        "src/agents/cancellation",
        "src/agents/complaint",
        "src/agents/policy",
        "src/agents/service",
        "src/agents/sql",
        "src/agents/tools",
        
        # NLP directories
        "src/nlp",
        "src/nlp/intent",
        "src/nlp/ner",
        "src/nlp/sentiment",
        "src/nlp/models",
        
        # RAG directories
        "src/rag",
        "src/rag/embeddings",
        "src/rag/retrieval",
        "src/rag/prompts",
        "src/rag/vector_store",
        
        # LLM directories
        "src/llm",
        "src/llm/gemini",
        "src/llm/prompts",
        "src/llm/cache",
        
        # Monitoring directories
        "src/monitoring",
        "src/monitoring/metrics",
        "src/monitoring/logging",
        "src/monitoring/tracing",
        
        # Evaluation directories
        "src/evaluation",
        "src/evaluation/datasets",
        "src/evaluation/metrics",
        
        # Background tasks
        "src/tasks",
        "src/tasks/celery_app",
        "src/tasks/workers",
        
        # Test directories
        "tests",
        "tests/unit",
        "tests/unit/api",
        "tests/unit/agents",
        "tests/unit/services",
        "tests/unit/repositories",
        "tests/integration",
        "tests/integration/api",
        "tests/integration/database",
        "tests/e2e",
        "tests/fixtures",
        
        # Data directories
        "data",
        "data/uploads",
        "data/cache",
        "data/models",
        "data/vector_store",
        "data/temp",
        
        # Config directories
        "config",
        "config/environments",
        
        # Logs directory
        "logs",
        
        # Scripts directory
        "scripts",
        "scripts/migrations",
        "scripts/seeds",
    ]
    
    # Create directories
    print("Creating directory structure...")
    for directory in directories:
        dir_path = backend_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    # Create __init__.py files
    print("\nCreating __init__.py files...")
    init_files = [
        "src/__init__.py",
        "src/config/__init__.py",
        "src/models/__init__.py",
        "src/schemas/__init__.py",
        "src/repositories/__init__.py",
        "src/services/__init__.py",
        "src/middleware/__init__.py",
        "src/utils/__init__.py",
        "src/api/__init__.py",
        "src/api/v1/__init__.py",
        "src/api/v1/endpoints/__init__.py",
        "src/api/v1/dependencies/__init__.py",
        "src/api/middleware/__init__.py",
        "src/core/__init__.py",
        "src/core/database/__init__.py",
        "src/core/cache/__init__.py",
        "src/core/security/__init__.py",
        "src/core/models/__init__.py",
        "src/core/repositories/__init__.py",
        "src/core/services/__init__.py",
        "src/agents/__init__.py",
        "src/agents/base/__init__.py",
        "src/agents/coordinator/__init__.py",
        "src/agents/booking/__init__.py",
        "src/agents/cancellation/__init__.py",
        "src/agents/complaint/__init__.py",
        "src/agents/policy/__init__.py",
        "src/agents/service/__init__.py",
        "src/agents/sql/__init__.py",
        "src/agents/tools/__init__.py",
        "src/nlp/__init__.py",
        "src/nlp/intent/__init__.py",
        "src/nlp/ner/__init__.py",
        "src/nlp/sentiment/__init__.py",
        "src/nlp/models/__init__.py",
        "src/rag/__init__.py",
        "src/rag/embeddings/__init__.py",
        "src/rag/retrieval/__init__.py",
        "src/rag/prompts/__init__.py",
        "src/rag/vector_store/__init__.py",
        "src/llm/__init__.py",
        "src/llm/gemini/__init__.py",
        "src/llm/prompts/__init__.py",
        "src/llm/cache/__init__.py",
        "src/monitoring/__init__.py",
        "src/monitoring/metrics/__init__.py",
        "src/monitoring/logging/__init__.py",
        "src/monitoring/tracing/__init__.py",
        "src/evaluation/__init__.py",
        "src/evaluation/datasets/__init__.py",
        "src/evaluation/metrics/__init__.py",
        "src/tasks/__init__.py",
        "src/tasks/celery_app/__init__.py",
        "src/tasks/workers/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/unit/api/__init__.py",
        "tests/unit/agents/__init__.py",
        "tests/unit/services/__init__.py",
        "tests/unit/repositories/__init__.py",
        "tests/integration/__init__.py",
        "tests/integration/api/__init__.py",
        "tests/integration/database/__init__.py",
        "tests/e2e/__init__.py",
        "tests/fixtures/__init__.py",
    ]
    
    for init_file in init_files:
        file_path = backend_root / init_file
        if not file_path.exists():
            file_path.write_text('"""Package initialization."""\n')
            print(f"✓ Created: {init_file}")
        else:
            print(f"⊙ Exists: {init_file}")
    
    print("\n✅ Directory structure setup complete!")


if __name__ == "__main__":
    create_directory_structure()

