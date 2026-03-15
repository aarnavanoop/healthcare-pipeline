An end-to-end data engineering pipeline built with Python, Docker, and PostgreSQL. 
Generates synthetic patient vitals using SDV/MEG, injects deliberate anomalies for 
downstream ML detection, and loads the dataset into a local PostgreSQL database.
Phase 1 (local foundation) is in active development. AWS cloud migration (Phase 2) 
and ML anomaly detection with FastAPI serving (Phase 3) follow.

Phase 1 in development:
## Local Development Environment

This project uses Docker to manage its Python environment and dependencies. 

### Prerequisites
Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your machine.

### 1. Build the Image
If you are running this for the first time, or if you have added new libraries to the `Dockerfile`, build the image by running:
`docker build -t my-data-env .`

### 2. Run Jupyter Notebook
To start up the environment and launch Jupyter Notebook, run the following command:
`docker run -p 8888:8888 my-data-env jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root`

Once the server starts, hold `Command` and click the `127.0.0.1` link in your terminal to open Jupyter in your browser. To shut down the container, press `Ctrl+C` in your terminal.