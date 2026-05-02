# AI-Powered Patient Triage & RAG Engine

## Problem Statement
This project architects a decoupled, full-stack AI application designed to securely process synthetic patient telemetry and serve critical medical insights via a Retrieval-Augmented Generation (RAG) pipeline. By engineering a hardened PostgreSQL database based on the UCI Heart Disease dataset, this system provides a highly concurrent, privacy-compliant backend that grounds Large Language Models in verifiable clinical data.

## Architecture & Design Decisions
![Architecture Diagram Placeholder](./architecture.png)
*(Diagram to be updated upon App Runner Deployment in Phase 4)*

**Architectural Note (Decoupled Design):** This project intentionally separates the backend engine from the presentation layer to mimic modern enterprise software environments. 
* **The Engine (Python/FastAPI):** Handles all business logic, asynchronous database connections, and AI orchestration.
* **The Memory (PostgreSQL + pgvector):** Serves as the strict relational store and the vector database for LLM similarity search.
* **The Interface (React):** A thin presentation layer that consumes RESTful endpoints and streams Server-Sent Events (SSE).

## Tech Stack
* **Backend:** Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2
* **Authentication:** JWT (python-jose), bcrypt, passlib
* **Database:** PostgreSQL, `pgvector` extension
* **AI/ML:** OpenAI API, SDV Gaussian Copula (Synthetic Generation)
* **Frontend:** React (Vite), Tailwind CSS
* **Infrastructure:** Docker Compose, GitHub Actions, AWS App Runner

## Project Status: Phase 2 — The API Engine (Completed)

Phase 2 focused on building a production-grade, asynchronous RESTful API on top of the Phase 1 PostgreSQL database. Every design decision prioritized correctness, strict validation, and engineering maturity over speed.

### Phase 2 Progress Checklist
- [x] **Async Architecture:** Implemented `asyncpg` and asynchronous SQLAlchemy sessions to prevent event-loop blocking during I/O operations.
- [x] **Strict Type Validation:** Engineered comprehensive Pydantic v2 schemas for all request/response bodies, including a fully nested `VitalsSchema`.
- [x] **JWT Authentication Flow:** Built secure `/auth/register` (bcrypt hashing) and `/auth/login` (OAuth2PasswordRequestForm) endpoints.
- [x] **Route Protection:** Created a robust `get_current_user` dependency to lock down all `/patients` routes via JWT Bearer validation.
- [x] **Production Guardrails:** Configured `slowapi` for IP-based rate limiting (100 req/min) and custom global exception handlers (422, 500) to ensure predictable JSON responses and prevent HTML stack-trace leakage.
- [x] **Integration Testing Suite:** Achieved 100% test coverage for Phase 2 using Pytest. Overcame async database leakage by isolating the `TestClient` within context managers and strategically utilizing FastAPI's `dependency_overrides` for isolated authentication bypass.

### Phase 1 Progress Checklist (Completed)
- [x] Docker environment configured (Python App + PostgreSQL Database).
- [x] ETL Pipeline executed on UCI Heart Disease dataset (`StandardScaler` normalization, categorical encoding).
- [x] SDV Gaussian Copula trained to generate 3,000 synthetic patient records (Diagnostic Quality: 89.64%).
- [x] Deliberate clinical anomalies injected into 5% of data.
- [x] Hardened PostgreSQL schema (UUIDs, `NOT NULL` constraints).

## Upcoming Phases
* **Phase 3 (Weeks 7-9):** Vectorizing synthetic doctor's notes, `pgvector` similarity search, and manual LLM RAG integration (no LangChain).
* **Phase 4 (Weeks 10-12):** React dashboard development, SSE streaming chat, and AWS App Runner CI/CD deployment.

## Local Setup & API Execution
Ensure Docker Desktop is installed and running on your machine.

**1. Spin up the infrastructure:**
```bash
docker compose up -d --build

## Local Setup & Execution
Ensure Docker Desktop is installed and running on your machine.

**1. Spin up the infrastructure:**
`docker compose up -d`

**2. Run the end-to-end data foundation pipeline:**
`docker compose exec app python pipeline.py`

**3. Verify the database load:**
`docker compose exec db psql -U admin -d healthcare -c "SELECT COUNT(*) FROM healthcare_data.patients;"`

**4. Shut down the environment:**
`docker compose down`