"""
Prometheus metrics for ConvergeAI application

This module defines all Prometheus metrics for monitoring:
- HTTP request metrics
- Agent execution metrics
- LLM usage metrics
- Database metrics
- RAG/Pinecone metrics
- Business metrics
"""
import logging
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, REGISTRY

logger = logging.getLogger(__name__)

# Use default registry
metrics_registry = REGISTRY

# ============================================
# HTTP/API METRICS
# ============================================

# Total HTTP requests
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=metrics_registry
)

# HTTP request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=metrics_registry
)

# HTTP requests in progress
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint'],
    registry=metrics_registry
)

# ============================================
# AGENT METRICS
# ============================================

# Total agent executions
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_name', 'intent', 'status'],
    registry=metrics_registry
)

# Agent execution duration
agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_name', 'intent'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
    registry=metrics_registry
)

# Agent errors
agent_errors_total = Counter(
    'agent_errors_total',
    'Total agent errors',
    ['agent_name', 'error_type'],
    registry=metrics_registry
)

# Agent concurrent executions
agent_concurrent_executions = Gauge(
    'agent_concurrent_executions',
    'Number of concurrent agent executions',
    ['agent_name'],
    registry=metrics_registry
)

# ============================================
# LLM METRICS
# ============================================

# Total LLM requests
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'operation'],
    registry=metrics_registry
)

# LLM tokens used
llm_tokens_used_total = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model', 'token_type'],
    registry=metrics_registry
)

# LLM request duration
llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['model', 'operation'],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
    registry=metrics_registry
)

# LLM errors
llm_errors_total = Counter(
    'llm_errors_total',
    'Total LLM errors',
    ['model', 'error_type'],
    registry=metrics_registry
)

# ============================================
# DATABASE METRICS
# ============================================

# Total database queries
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table'],
    registry=metrics_registry
)

# Database query duration
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
    registry=metrics_registry
)

# Database connections
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=metrics_registry
)

# Database connection pool size
db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    registry=metrics_registry
)

# ============================================
# RAG/PINECONE METRICS
# ============================================

# Total RAG retrievals
rag_retrievals_total = Counter(
    'rag_retrievals_total',
    'Total RAG retrievals',
    ['namespace', 'status'],
    registry=metrics_registry
)

# RAG retrieval duration
rag_retrieval_duration_seconds = Histogram(
    'rag_retrieval_duration_seconds',
    'RAG retrieval duration in seconds',
    ['namespace'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0),
    registry=metrics_registry
)

# RAG chunks retrieved
rag_chunks_retrieved = Histogram(
    'rag_chunks_retrieved',
    'Number of chunks retrieved per query',
    ['namespace'],
    buckets=(1, 3, 5, 7, 10, 15, 20),
    registry=metrics_registry
)

# RAG grounding score
rag_grounding_score = Histogram(
    'rag_grounding_score',
    'RAG response grounding score',
    ['agent_name'],
    buckets=(0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=metrics_registry
)

# ============================================
# BUSINESS METRICS
# ============================================

# Total bookings created
bookings_created_total = Counter(
    'bookings_created_total',
    'Total bookings created',
    ['service_category', 'status'],
    registry=metrics_registry
)

# Total complaints created
complaints_created_total = Counter(
    'complaints_created_total',
    'Total complaints created',
    ['priority', 'status'],
    registry=metrics_registry
)

# Total chat sessions
chat_sessions_total = Counter(
    'chat_sessions_total',
    'Total chat sessions',
    ['user_type'],
    registry=metrics_registry
)

# Total user registrations
user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    registry=metrics_registry
)

# Active users
active_users = Gauge(
    'active_users',
    'Number of active users',
    registry=metrics_registry
)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_metrics_registry():
    """Get the Prometheus metrics registry"""
    return metrics_registry


logger.info("Prometheus metrics initialized")

