# Healthcare Data Engineering Pipeline

## Problem Statement
This project architects an end-to-end, AWS-native Data Engineering pipeline designed to generate, process, evaluate, and securely serve synthetic patient telemetry data. By engineering synthetic vitals based on the UCI Heart Disease dataset, this pipeline provides a safe, privacy-compliant foundation for downstream healthcare machine learning models.

## Architecture & Design Decisions
![Architecture Diagram Placeholder](./architecture.png)
*(Diagram coming at the end of Phase 2)*

**Architectural Note (OLTP vs. OLAP):** This project intentionally separates the operational database from the analytical warehouse to mimic enterprise data environments. 
* **PostgreSQL (Local / AWS RDS)** serves purely as the transactional store (OLTP), enforcing strict schema rules and handling structured row inserts from the pipeline. 
* **AWS Redshift** serves as the analytical data warehouse (OLAP), handling complex queries and acting as the transformation target for dbt models.

## Tech Stack
* **Python & Pandas:** Core data extraction, transformation, and cleaning logic.
* **Docker Compose:** Multi-container orchestration to ensure environment reproducibility across local and cloud environments.
* **PostgreSQL:** Relational database for structured OLTP storage, enforcing UUID primary keys and data integrity constraints.
* **Synthetic Data Generator (SDV):** Generates statistically plausible patient telemetry using the `GaussianCopulaSynthesizer`.
* **SQLAlchemy & psycopg2:** Database connection and data loading engine.
* **Upcoming (Phases 2-4):** AWS S3, AWS Redshift, dbt, scikit-learn (Isolation Forest), MLflow, FastAPI, GitHub Actions, AWS App Runner.

## Project Status: Phase 1 — Local Foundation (Completed)

### Progress Checklist
- [x] Docker environment configured (Python App + PostgreSQL Database).
- [x] UCI Heart Disease dataset ingested and explored.
- [x] **ETL Pipeline:** Handled nulls via imputation, one-hot encoded categorical variables, and normalized numeric columns using `StandardScaler`.
- [x] **Synthetic Data Generation:** Trained an SDV Gaussian Copula model to generate 3,000 synthetic patient records. Diagnostic quality score achieved: **89.64%**.
- [x] **Anomaly Injection:** Engineered deliberate clinical anomalies (extreme standard deviations) into 5% of the data to serve as ground-truth test cases for future unsupervised ML detection.
- [x] **Database Architecture:** Designed a hardened PostgreSQL schema featuring universally unique identifiers (UUIDs), strict typing, and `NOT NULL` constraints.
- [x] **Automated Orchestration:** Developed `pipeline.py` to automate the end-to-end workflow (Extract -> Clean -> Generate -> Inject -> Load) in a single command.

## Local Setup & Execution
Ensure Docker Desktop is installed and running on your machine.

**1. Spin up the infrastructure:**
`docker compose up -d`

**2. Run the end-to-end data pipeline:**
`docker compose exec app python pipeline.py`

**3. Verify the database load:**
`docker compose exec db psql -U admin -d healthcare -c "SELECT COUNT(*) FROM healthcare_data.patients;"`

**4. Shut down the environment:**
`docker compose down`