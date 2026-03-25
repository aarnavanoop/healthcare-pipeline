# Healthcare Data Engineering Pipeline

## Problem Statement
This project architects an end-to-end, AWS-native Data Engineering pipeline designed to generate, process, evaluate, and securely serve synthetic patient telemetry data. By engineering synthetic vitals based on the UCI Heart Disease dataset, this pipeline provides a safe, privacy-compliant foundation for healthcare machine learning models.

## Architecture & Design Decisions
![Architecture Diagram Placeholder](./architecture.png)
*(Diagram coming at the end of Phase 2)*

**Architectural Note (OLTP vs. OLAP):** This project intentionally separates the operational database from the analytical warehouse. 
***AWS RDS (PostgreSQL)** serves purely as the transactional store (OLTP), handling structured row inserts from the ETL pipeline. 
***AWS Redshift** serves as the analytical data warehouse (OLAP), handling complex queries and acting as the transformation target for our dbt models.

## Tech Stack
* **Python & Pandas:** Core data extraction, transformation, and cleaning logic.
* **Docker:** Containerization to ensure environment reproducibility across local and cloud environments.
* **PostgreSQL (Local & AWS RDS):** Relational database for OLTP storage.
* **Synthetic Data Generator (SDV):** Generates statistically plausible patient telemetry using the GaussianCopula synthesizer.
* **scikit-learn:** Used for data normalization (StandardScaler) and anomaly detection (Isolation Forest).
* **Upcoming (Phases 2-4):** AWS S3, AWS Redshift, dbt, FastAPI, MLflow, GitHub Actions, AWS App Runner.

## Project Status: Phase 1 — Local Foundation (In Progress)

### Progress Checklist
- [x] Docker environment configured with Jupyter Notebook
- [x] UCI Heart Disease dataset loaded and explored
- [x] **ETL Pipeline:** Handled nulls (medians), encoded categoricals (one-hot), and normalized numeric columns (StandardScaler).
- [x] **Synthetic Data Generation:** Implemented SDV GaussianCopulaSynthesizer generating 3,000 synthetic patient records. Diagnostic quality score achieved: 89.64%.
- [ ] Deliberate anomaly injection 
- [ ] PostgreSQL schema creation and local data load

## Local Setup
Make sure Docker Desktop is installed and running.

Build the image:
`docker build -t healthcare-pipeline .`

Run the container:
`docker run -p 8888:8888 -v $(pwd):/app healthcare-pipeline`

Open the localhost:8888 link in your terminal to access Jupyter.