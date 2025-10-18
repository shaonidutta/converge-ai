"""
Pytest configuration and shared fixtures for all tests

This file is automatically loaded by pytest and provides:
- Environment variable setup for tests
- Shared fixtures
- Test configuration
"""

import os
import pytest


# ============================================================
# ENVIRONMENT SETUP (runs before any imports)
# ============================================================

def pytest_configure(config):
    """
    Configure pytest environment before tests run
    
    Sets up test environment variables to avoid validation errors
    """
    # Set test environment variables if not already set
    test_env_vars = {
        'DATABASE_URL': 'sqlite+aiosqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-for-testing-only',
        'PINECONE_API_KEY': 'test-pinecone-api-key',
        'GOOGLE_API_KEY': 'test-google-api-key',
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'PINECONE_INDEX_NAME': 'test-index',
        'PINECONE_ENVIRONMENT': 'us-east-1',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ENVIRONMENT': 'development'  # Must be one of: development, staging, production
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value


# ============================================================
# SHARED FIXTURES
# ============================================================

@pytest.fixture
def test_env_vars():
    """
    Fixture that provides test environment variables

    Usage:
        def test_something(test_env_vars):
            assert test_env_vars['DATABASE_URL'] == 'sqlite+aiosqlite:///:memory:'
    """
    return {
        'DATABASE_URL': 'sqlite+aiosqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-for-testing-only',
        'PINECONE_API_KEY': 'test-pinecone-api-key',
        'GOOGLE_API_KEY': 'test-google-api-key',
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'PINECONE_INDEX_NAME': 'test-index',
        'PINECONE_ENVIRONMENT': 'us-east-1',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ENVIRONMENT': 'development'
    }


# ============================================================
# PYTEST CONFIGURATION
# ============================================================

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers
    
    Automatically marks tests based on their location:
    - tests/unit/* -> @pytest.mark.unit
    - tests/integration/* -> @pytest.mark.integration
    - tests/performance/* -> @pytest.mark.performance
    - tests/e2e/* -> @pytest.mark.e2e
    """
    for item in items:
        # Get test file path
        test_path = str(item.fspath)
        
        # Add markers based on directory
        if '/unit/' in test_path or '\\unit\\' in test_path:
            item.add_marker(pytest.mark.unit)
        elif '/integration/' in test_path or '\\integration\\' in test_path:
            item.add_marker(pytest.mark.integration)
        elif '/performance/' in test_path or '\\performance\\' in test_path:
            item.add_marker(pytest.mark.performance)
        elif '/e2e/' in test_path or '\\e2e\\' in test_path:
            item.add_marker(pytest.mark.e2e)

