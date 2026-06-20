# AI-Powered Patient Triage & RAG Engine

A full-stack AI patient triage system: a hardened PostgreSQL data foundation, an async FastAPI backend, a Retrieval-Augmented Generation pipeline built from first principles, and a React frontend — containerised end-to-end with Docker Compose and tested via GitHub Actions CI/CD on every push.

## Problem Statement
Hospitals generate constant streams of patient vitals, but the bottleneck isn't collecting that data — it's acting on it quickly. This project builds a system that stores structured patient data, automatically flags anomalous vitals, and gives a clinician an AI chat interface to ask natural-language questions and get answers grounded in real patient notes — not hallucinated ones.

## Architecture & Design Decisions

This project intentionally separates the backend engine from the presentation layer to mirror a modern enterprise environment:

* **The Engine (Python/FastAPI):** All business logic, async database connections, and AI orchestration.
* **The Memory (PostgreSQL + pgvector):** The relational store and the vector database for LLM similarity search, in one place.
* **The Interface (React):** A thin presentation layer that consumes REST endpoints and streams Server-Sent Events.

A few decisions worth calling out:
* **No LangChain.** The RAG pipeline (embed → retrieve → inject → generate) is written and tested as four explicit functions. Understanding what an abstraction layer does is more transferable than knowing how to configure it.
* **Redis + arq over FastAPI's `BackgroundTasks`.** Embedding jobs run in a separate worker process so a crash or restart doesn't lose work or affect the API process.
* **JWT stored in React context, not `localStorage`.** Avoids exposing the token to XSS-injected scripts.
* **Every RAG query is audited.** Query, retrieved context, response, and latency are logged to a `rag_audit` table — non-negotiable in a clinical context where AI outputs need to be traceable.

## Tech Stack
* **Backend:** Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2
* **Authentication:** JWT (python-jose), bcrypt, passlib
* **Database:** PostgreSQL, `pgvector` extension
* **AI/ML:** OpenAI API (`text-embedding-3-small`, `gpt-4o-mini`) — direct SDK, no LangChain
* **Task Queue:** Redis + arq (async background embedding jobs)
* **Real-time:** Server-Sent Events (streaming chat), WebSockets (live anomaly alerts)
* **Frontend:** React (Vite), Tailwind CSS
* **Infrastructure:** Docker Compose (4 services), GitHub Actions CI/CD

## Project Status: Complete — All 4 Phases Shipped

### Phase 1 — Data Foundation
- [x] Docker environment (Python app + PostgreSQL).
- [x] ETL pipeline on the UCI Heart Disease dataset (`StandardScaler` normalisation, categorical encoding, outlier handling).
- [x] SDV Gaussian Copula trained to generate 3,000 synthetic patient records (89.64% diagnostic quality).
- [x] Deliberate clinical anomalies injected into 5% of records as ground-truth labels.
- [x] Hardened PostgreSQL schema (UUID primary keys, `NOT NULL` constraints).

### Phase 2 — The API Engine
- [x] Async FastAPI app with `asyncpg` + async SQLAlchemy sessions — no event-loop blocking on I/O.
- [x] Pydantic v2 schemas for every request/response, including nested vitals.
- [x] JWT auth flow — `/auth/register` (bcrypt) and `/auth/login` (OAuth2PasswordRequestForm).
- [x] `get_current_user` dependency locking down all `/patients` routes.
- [x] Rate limiting via `slowapi` (100 req/min, stricter limits on auth endpoints) + custom exception handlers — every error returns structured JSON, never a stack trace.
- [x] Integration test suite (Pytest) — 100% coverage on Phase 2, using `dependency_overrides` to isolate auth and database state in tests.

### Phase 3 — AI & Vector Search
- [x] PostgreSQL upgraded to `pgvector/pgvector:pg15`; `patient_notes` table with `vector(1536)` column and `rag_audit` logging table.
- [x] Synthetic clinical notes generated per anomalous patient (GPT-4o-mini, grounded in real vitals) and embedded with `text-embedding-3-small`.
- [x] Manual RAG pipeline (`app/rag/pipeline.py`) — embed query → cosine similarity search in pgvector (top-3) → inject context into system prompt → stream generation. Constrained to answer only from retrieved notes.
- [x] `POST /api/chat` — SSE streaming chat response.
- [x] `/ws/alerts` — WebSocket endpoint broadcasting live anomaly notifications.
- [x] Redis + arq background task queue for async note generation/embedding on new patient ingestion.
- [x] Full test suite: unit tests (embedding, retrieval, prompt construction), integration tests, and a RAG pipeline test with mocked OpenAI calls — all run in CI.

### Phase 4 — Frontend & Deployment
- [x] React (Vite) + Tailwind frontend — Login, Patient Dashboard, Patient Detail.
- [x] JWT auth flow wired end-to-end; token kept in React context, not `localStorage`.
- [x] Patient Dashboard — real paginated/filtered data from `/patients/anomalies`, severity badges.
- [x] Patient Detail — vitals with colour-coded thresholds + SSE streaming AI chat, rendered token by token.
- [x] Full Docker Compose stack — frontend (multi-stage `node:18-alpine` → `nginx:alpine`), backend, postgres, redis.
- [x] GitHub Actions CI/CD — push to `main` → pytest → build frontend and backend Docker images, every push tested and built green.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service health check |
| `/auth/register` | POST | New user registration |
| `/auth/login` | POST | User authentication — returns JWT |
| `/patients` | GET | Paginated patient list with filters |
| `/patients/{id}` | GET | Single patient detail |
| `/patients/anomalies` | GET | Filtered anomalous patient records |
| `/api/chat` | POST | RAG-powered chat with SSE streaming |
| `/ws/alerts` | WS | Live anomaly notifications |

Full schemas for every endpoint are available at `/docs` (Swagger UI).

## Local Setup & Execution
Ensure Docker Desktop is installed and running.

**1. Spin up the full stack:**
```bash
docker compose up -d --build
```

**2. Run the end-to-end data foundation pipeline (first run only):**
```bash
docker compose exec app python pipeline.py
```

**3. Verify the database load:**
```bash
docker compose exec db psql -U admin -d healthcare -c "SELECT COUNT(*) FROM healthcare_data.patients;"
```

**4. Access the app:**
- Frontend: `localhost:3000`
- Backend API + Swagger docs: `localhost:8000/docs`

**5. Shut down the environment:**
```bash
docker compose down
```

## What I'd Improve With More Time
- Deploy to a live public endpoint (AWS App Runner or equivalent) so the system is reachable outside local Docker.
- Terraform for infrastructure-as-code instead of manually provisioned AWS resources.
- Expanded RAG evaluation (retrieval precision/recall metrics, not just qualitative review).
- A second vector index strategy (HNSW) benchmarked against the current approach at larger scale.
- OAuth2 / SSO instead of a standalone JWT auth flow, to reflect real hospital-system identity providers.