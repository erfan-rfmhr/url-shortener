# Scalability Guide

Let's dive into scalable solutions.

## Heavy Logging

### Background tasks

FastAPI BackgroundTasks enqueue logs and remove I/O cost from the path.

### Async workers

- Use Celery and Redis/RabbitMQ: pass logs to Celery workers and let them handle the queue.
- Batching: gather logs from queue and bulk insert them into DB (like ClickHouse).

### Streaming

- Redis stream/Kafka: send logs to Redis stream/Kafka and consume them in real-time.
- ClickHouse or OpenSearch: use databases with capability of performing as Kafka consumer.
- Prometheus metrics: use Prometheus to monitor the application and collect histogram metrics.

## Multi-instance

- Caching with Redis.
- Use RabbitMQ/Kafka for handling logs, events and slow jobs.
- Decouple migrations and run them as pre-deploy step.
- Advanced configuration of uvicorn/gunicorn workers.
- Advanced hash functions for creating short codes with more uniqueness guaranty.
- Decouple environment variables.
- Use kubernetes for deployment and autoscaling.

## High-traffic campaign

- Serve redirection on edge servers:
  - a reverse proxy that performs a Redis GET and issues redirect response on hit.
- Warm cache for top codes: pre-populate cache with top codes before the traffic starts.
- Rate limiting: use Redis to limit the number of requests per user.
- Database replication: one primary as write database, and many replicas as read databases:
  - Data pipeline between primary and secondary databases is needed to sync data between them.
  - Repopulating cache from primary database on each cache miss.
- Configure timeouts.
- Connection pooling: use PgBouncer or other connection pooling tools to handle database connections efficiently.
- Write-behind on primary: Batch writes to the primary database and send them to the replicas asynchronously.
- Autoscaling using Kubernetes: use Kubernetes to scale the application based on the traffic and load balancing between instances.
- Streaming events using Kafka/Redis stream: send events to Kafka/Redis stream and consume them in real-time using databases like ClickHouse.
