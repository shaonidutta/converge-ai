"""
Pytest configuration for unit tests
"""

import os
import sys
from pathlib import Path

# Set test environment variables before importing any modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test_jwt_secret_key_for_testing_only")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only")
os.environ.setdefault("PINECONE_API_KEY", "test_pinecone_key")
os.environ.setdefault("GOOGLE_API_KEY", "test_google_key")
os.environ.setdefault("ENVIRONMENT", "development")

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

