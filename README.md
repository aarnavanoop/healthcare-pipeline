# Healthcare Data Engineering Pipeline

An end-to-end data engineering pipeline that generates synthetic patient 
data using the MEG framework and detects anomalies using machine learning.

## Project Status
Phase 1 — Local Foundation (In Progress)

## Progress
- [x] Docker environment configured with Jupyter Notebook
- [x] UCI Heart Disease dataset (Cleveland) loaded and explored
- [x] Dataset structure understood: 303 patients, 14 columns
- [x] Hidden null values identified in Number of Major Vessels (4) and Thal (2)
- [ ] ETL cleaning script
- [ ] Synthetic data generation via MEG
- [ ] Anomaly injection
- [ ] PostgreSQL schema and load

## Local Setup
Make sure Docker Desktop is installed and running.

Build the image:
docker build -t healthcare-pipeline .

Run the container:
docker run -p 8888:8888 -v $(pwd):/app healthcare-pipeline

Open the localhost:8888 link in your terminal to access Jupyter.

## Tech Stack
Python · pandas · Docker · PostgreSQL (coming Phase 1)
AWS S3 · Redshift · dbt · FastAPI · MLflow (coming Phase 2-4)