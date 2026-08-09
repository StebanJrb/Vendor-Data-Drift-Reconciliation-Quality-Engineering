# Self-contained execution-layer image for this project. Orchestrator-
# agnostic: reads its configuration from environment variables, runs the
# pipeline for one vendor-drop month, and communicates success/failure
# purely through the process exit code (see src/main.py). It has no
# knowledge of Airflow or any other scheduler — an external orchestrator
# (this portfolio's separate `orchestration-hub` repo) is responsible for
# scheduling this image and reacting to its exit code.
#
# Build:  docker build -t vendor-drift-pipeline .
# Run:    docker run --rm --env-file .env -e YEAR_MONTH=2023-07 vendor-drift-pipeline

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY schema_registry/ ./schema_registry
COPY great_expectations/ ./great_expectations

ENTRYPOINT ["python", "-m", "src.main"]
