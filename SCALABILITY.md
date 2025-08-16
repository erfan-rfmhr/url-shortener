# Scalability Guide

Let's dive into scalable solutions.

## Heavy Logging

### Background tasks

FastAPI BackgroundTasks enqueue logs and remove I/O cost from the path.

### Async workers

- Use Celery and Redis/RabbitMQ.
- Batching: bulk insert logs into DB (ClickHouse)

### Streaming

- Redis stream/Kafka for streaming logs.
- ClickHouse or OpenSearch for storing and analytics (OLAP).
- Prometheus metrics as observability.

## Multi-instance

- Caching with Redis.
- Use RabbitMQ/Kafka for handling logs, events and slow jobs.
- Decouple migrations and run them as pre-deploy step.
- Advanced configuration of uvicorn/gunicorn workers.
- Advanced hash functions for creating short codes with more uniqueness guaranty.
- Decouple environment variables.

## High-traffic campaign

- Serve redirection on edge servers:
  - a reverse proxy that performs a Redis GET and issues redirect response on hit.
- Warm cache for top codes.
- Rate limiting.
- Database replication. One primary as write database, and many replicas as read databases:
  - Data pipeline between primary and slaves is needed.
  - Repopulating cache from Database on each cache miss.
- Configure timeouts.
- Connection pooling, like PgBouncer.
- With write-behind on primary, writes are batched and Database doesn't get hit on every request.
- Autoscaling using Kubernetes.
- Streaming events using Kafka/Redis stream.
