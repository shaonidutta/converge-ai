# ConvergeAI Monitoring Setup Guide

## Overview

This guide explains how to set up and use Prometheus + Grafana monitoring for ConvergeAI.

## Architecture

```
┌─────────────────┐
│  FastAPI App    │
│  (Port 8000)    │
│  /api/v1/metrics│
└────────┬────────┘
         │ scrapes every 15s
         ▼
┌─────────────────┐
│   Prometheus    │
│   (Port 9090)   │
│  - Stores metrics
│  - Evaluates alerts
└────────┬────────┘
         │ queries
         ▼
┌─────────────────┐
│    Grafana      │
│   (Port 3000)   │
│  - Visualizes
│  - Dashboards
└─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Monitoring Stack

```bash
cd deployment
docker-compose -f docker-compose.monitoring.yml up -d
```

This starts:
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3000

### 3. Start FastAPI Application

```bash
cd backend
python -m uvicorn src.main:app --reload
```

### 4. Access Dashboards

**Grafana:**
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`
- Dashboard: "ConvergeAI - System Overview"

**Prometheus:**
- URL: http://localhost:9090
- Metrics endpoint: http://localhost:8000/api/v1/metrics

## Metrics Collected

### HTTP/API Metrics
- `http_requests_total` - Total HTTP requests (by method, endpoint, status_code)
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Current requests in progress

### Agent Metrics
- `agent_executions_total` - Total agent executions (by agent_name, intent, status)
- `agent_execution_duration_seconds` - Agent execution duration histogram
- `agent_errors_total` - Total agent errors (by agent_name, error_type)
- `agent_concurrent_executions` - Current concurrent agent executions

### LLM Metrics
- `llm_requests_total` - Total LLM requests (by model, operation)
- `llm_tokens_used_total` - Total tokens used (by model, token_type)
- `llm_request_duration_seconds` - LLM request duration histogram
- `llm_errors_total` - Total LLM errors

### Database Metrics
- `db_queries_total` - Total database queries (by operation, table)
- `db_query_duration_seconds` - Query duration histogram
- `db_connections_active` - Active database connections
- `db_connection_pool_size` - Connection pool size

### RAG Metrics
- `rag_retrievals_total` - Total RAG retrievals (by namespace, status)
- `rag_retrieval_duration_seconds` - Retrieval duration histogram
- `rag_chunks_retrieved` - Number of chunks retrieved
- `rag_grounding_score` - Response grounding score histogram

### Business Metrics
- `bookings_created_total` - Total bookings created
- `complaints_created_total` - Total complaints created
- `chat_sessions_total` - Total chat sessions
- `user_registrations_total` - Total user registrations
- `active_users` - Current active users

## Alert Rules

Prometheus evaluates these alert rules:

### Critical Alerts
- **HighErrorRate**: Error rate > 5% for 5 minutes
- **APIDown**: API unreachable for 1 minute
- **HighLLMErrorRate**: LLM error rate > 5% for 5 minutes

### Warning Alerts
- **HighLatency**: p95 latency > 5s for 5 minutes
- **HighAgentErrorRate**: Agent error rate > 10% for 5 minutes
- **SlowAgentExecution**: Agent p95 > 10s for 5 minutes
- **SlowDatabaseQueries**: DB query p95 > 1s for 5 minutes
- **LowGroundingScore**: RAG grounding score median < 0.45 for 10 minutes

## Querying Metrics

### Prometheus Query Examples

**Request rate:**
```promql
rate(http_requests_total[5m])
```

**Error rate:**
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

**p95 latency:**
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

**Agent execution rate:**
```promql
sum(rate(agent_executions_total[5m])) by (agent_name)
```

**LLM token usage:**
```promql
sum(rate(llm_tokens_used_total[1h])) by (model)
```

## Health Checks

### Endpoints

1. **Basic Health**: `GET /health`
   - Always returns 200 if app is running

2. **Liveness**: `GET /api/v1/health/live`
   - Kubernetes liveness probe

3. **Readiness**: `GET /api/v1/health/ready`
   - Checks database, Pinecone, Redis
   - Returns 503 if any dependency is down

### Example

```bash
# Basic health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/api/v1/health/ready
```

## Grafana Dashboards

### System Overview Dashboard

Includes:
- Request rate and error rate
- Response time (p50, p95)
- Requests by endpoint
- Agent executions and duration
- LLM requests and token usage
- Database query performance
- RAG grounding scores

### Creating Custom Dashboards

1. Go to Grafana (http://localhost:3000)
2. Click "+" → "Dashboard"
3. Add panel
4. Select "Prometheus" as data source
5. Enter PromQL query
6. Configure visualization
7. Save dashboard

## Production Deployment

### 1. Update Prometheus Config

Edit `deployment/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'convergeai-backend'
    static_configs:
      - targets: ['your-api-domain.com:8000']
```

### 2. Secure Grafana

Change default password:

```yaml
# docker-compose.monitoring.yml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=<strong-password>
```

### 3. Enable HTTPS

Use reverse proxy (Nginx/Traefik) with SSL certificates.

### 4. Set Up Alerting

Configure Alertmanager for notifications:
- Email
- Slack
- PagerDuty
- Webhook

## Troubleshooting

### Metrics Not Showing

1. Check FastAPI is running:
   ```bash
   curl http://localhost:8000/api/v1/metrics
   ```

2. Check Prometheus targets:
   - Go to http://localhost:9090/targets
   - Ensure "convergeai-backend" is UP

3. Check Prometheus logs:
   ```bash
   docker logs convergeai-prometheus
   ```

### Grafana Not Connecting

1. Check Prometheus is running:
   ```bash
   curl http://localhost:9090/-/healthy
   ```

2. Check Grafana datasource:
   - Go to Configuration → Data Sources
   - Test connection

### High Memory Usage

Prometheus stores metrics in memory. To reduce:

1. Decrease retention time:
   ```yaml
   command:
     - '--storage.tsdb.retention.time=15d'  # Default: 30d
   ```

2. Reduce scrape frequency:
   ```yaml
   scrape_interval: 30s  # Default: 15s
   ```

## Next Steps

1. **Add Custom Metrics**: Instrument your code with custom metrics
2. **Create More Dashboards**: Agent-specific, business metrics, etc.
3. **Set Up Alerting**: Configure Alertmanager for notifications
4. **Add Tracing**: Integrate OpenTelemetry or Jaeger
5. **Log Aggregation**: Add ELK stack or Loki

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Grafana Dashboard Examples](https://grafana.com/grafana/dashboards/)

