#!/bin/bash

## need to 

echo "Building the image with Podman..."
podman build -t streamlit-agent-app -f Containerfile .

echo "Running the container..."
echo "App will be available at http://localhost:8501"
podman run --rm -p 8501:8501 --env-file .env localhost/streamlit-agent-app




# ── Langfuse v3 (self-hosted) ──
# Requires: PostgreSQL + ClickHouse + Langfuse server
# All containers share a pod so they communicate via localhost.

podman pod create --name langfuse-pod -p 3000:3000

podman run -d --pod langfuse-pod --name langfuse-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=langfuse docker.io/library/postgres:16-alpine

podman run -d --pod langfuse-pod --name langfuse-clickhouse -e CLICKHOUSE_DB=langfuse -e CLICKHOUSE_USER=clickhouse -e CLICKHOUSE_PASSWORD=clickhouse docker.io/clickhouse/clickhouse-server:latest

podman run -d --pod langfuse-pod --name langfuse-server -e DATABASE_URL=postgresql://postgres:postgres@localhost:5432/langfuse -e CLICKHOUSE_URL=http://clickhouse:clickhouse@localhost:8123/langfuse -e CLICKHOUSE_MIGRATION_URL=clickhouse://clickhouse:clickhouse@localhost:9000/langfuse -e CLICKHOUSE_USER=clickhouse -e CLICKHOUSE_PASSWORD=clickhouse -e CLICKHOUSE_CLUSTER_ENABLED=false -e NEXTAUTH_SECRET=any-random-secret-string-here -e NEXTAUTH_URL=http://localhost:3000 -e SALT=any-random-salt-string-here docker.io/langfuse/langfuse:latest