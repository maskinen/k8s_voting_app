# k8s_voting_app

A simple Kubernetes-friendly voting application consisting of multiple microservices, primarily built with Python, JavaScript, and Docker. The app is designed to demonstrate containerized service deployment and orchestration on Kubernetes.

## Overview

This project provides a distributed voting system with RESTful APIs to create voting rounds, cast votes, view results, and monitor service health and metrics.

### Components

- **vote** (Python/Flask):
  - Exposes APIs to create voting rounds, vote, close rounds, and retrieve results.
  - Tracks and exposes votes and round state using Prometheus metrics.
  - Connects to a PostgreSQL database for persistence.

- **result** (Node.js/Express):
  - Provides endpoints to check health and fetch results for voting rounds.
  - Aggregates results from the database.

- **worker** (Python/Flask):
  - Exposes health and metrics endpoints for background tasks or monitoring.
  - Provides a heartbeat metric for worker status.

- **db** (PostgreSQL):
  - Containerized database setup with initialization scripts for the voting schema.

## API Endpoints

### `vote` service (Python)
- `GET /health` — Health check.
- `POST /rounds` — Create a new voting round.
- `POST /vote` — Cast a vote (with optional `X-Voter-Id` header).
- `POST /rounds/<round_id>/close` — Close a voting round.
- `GET /rounds/<round_id>/results` — Get results for a round.
- `GET /metrics` — Prometheus metrics.

### `result` service (Node.js)
- `GET /health` — Health check.
- `GET /rounds/:id/results` — Get aggregated results for a round.

### `worker` service (Python)
- `GET /health` — Health check.
- `GET /metrics` — Worker heartbeat metrics.

## Running Locally

This repo is intended for use with Docker and Kubernetes. Each service has its own `Dockerfile`:

- `vote/Dockerfile` — Python API service.
- `result/Dockerfile` — Node.js results service.
- `worker/Dockerfile` — Python worker/metrics service.
- `db/Dockerfile` — PostgreSQL database with schema initialization.

You can build and run each service independently, or orchestrate them together using Kubernetes manifests.

## Language Breakdown

- Python — 72.5%
- JavaScript — 13.9%
- Dockerfile — 13.6%

## Database Schema

The PostgreSQL database stores voting rounds, options, and votes. Initialization is handled via the `init.sql` script (see `db/Dockerfile`).

## Metrics & Monitoring

All services expose Prometheus-compatible metrics endpoints for easy integration with monitoring solutions.

## License

MIT (or specify your license here)

---

This app is ideal for learning, prototyping, or demonstrating microservices deployment in Kubernetes environments.
