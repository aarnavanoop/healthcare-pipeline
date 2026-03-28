# AI-Powered Patient Triage & RAG Engine

## Problem Statement
This project architects a decoupled, full-stack AI application designed to securely process synthetic patient telemetry and serve critical medical insights via a Retrieval-Augmented Generation (RAG) pipeline. By engineering a hardened PostgreSQL database based on the UCI Heart Disease dataset, this system provides a highly concurrent, privacy-compliant backend that grounds Large Language Models in verifiable clinical data.

## Architecture & Design Decisions
![Architecture Diagram Placeholder](./architecture.png)
*(Diagram coming at the end of Phase 2)*

**Architectural Note (Decoupled Design):** This project intentionally separates the backend engine from the presentation layer to mimic modern enterprise software environments. 
* **The Engine (Python/FastAPI):** Handles all business logic, asynchronous database connections, and AI orchestration.
* **The Memory (PostgreSQL + pgvector):** Serves as the strict relational store and the vector database for LLM similarity search.
* **The Interface (React):** A thin presentation layer that consumes RESTful endpoints and streams Server-Sent Events (SSE).

## Tech Stack
* **Backend:** Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2
* **Database:** PostgreSQL, `pgvector` extension
* **AI/ML:** OpenAI API, LangChain, SDV Gaussian Copula (Synthetic Generation)
* **Frontend:** React (Vite), Tailwind CSS
* **Infrastructure:** Docker Compose, GitHub Actions, AWS App Runner

## Project Status: Phase 1 — Local Data Foundation (Completed)

### Progress Checklist
- [x] Docker environment configured (Python App + PostgreSQL Database).
- [x] UCI Heart Disease dataset ingested and explored.
- [x] **ETL Pipeline:** Handled nulls via imputation, one-hot encoded categorical variables, and normalized numeric columns using `StandardScaler`.
- [x] **Synthetic Data Generation:** Trained an SDV Gaussian Copula model to generate 3,000 synthetic patient records. Diagnostic quality score achieved: **89.64%**.
- [x] **Anomaly Injection:** Engineered deliberate clinical anomalies (extreme standard deviations) into 5% of the data to serve as ground-truth test cases for the upcoming AI retrieval system.
- [x] **Database Architecture:** Designed a hardened PostgreSQL schema featuring universally unique identifiers (UUIDs), strict typing, and `NOT NULL` constraints.
- [x] **Automated Orchestration:** Developed `pipeline.py` to automate the end-to-end data foundational workflow in a single command.

## Upcoming Phases
* **Phase 2 (Weeks 4-6):** FastAPI CRUD endpoint development, JWT Authentication, and async SQLAlchemy integration.
* **Phase 3 (Weeks 7-9):** Vectorizing synthetic doctor's notes, `pgvector` similarity search, and LLM RAG integration.
* **Phase 4 (Weeks 10-12):** React dashboard development, SSE streaming chat, and AWS App Runner CI/CD deployment.

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