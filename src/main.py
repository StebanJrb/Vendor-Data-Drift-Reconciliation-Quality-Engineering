# src/main.py
#
# Single entrypoint for this project's execution layer — what the root
# Dockerfile runs. It knows nothing about Airflow or any other
# orchestrator: it reads inputs from environment variables, runs the
# pipeline for one year-month, and reports success/failure purely through
# the process exit code. Scheduling, retries, and alerting on top of that
# exit code are the responsibility of the external orchestrator (this
# portfolio's separate `orchestration-hub` repo) — none of that belongs
# here.
#
# Required env vars (see .env.example), read via src.config.get_settings():
#   YEAR_MONTH               - "YYYY-MM", which vendor drop to process
#   MINIO_BUCKET_NAME, AWS_ENDPOINT_URL_S3,
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY  - MinIO/S3 access
#   WAREHOUSE_DB_URI (or POSTGRES_* parts)    - trusted warehouse + quarantine
#   MLFLOW_TRACKING_URI                       - quality metrics per run
#
# Exit codes:
#   0  -> pipeline completed and validation passed; warehouse updated
#   1  -> pipeline failed (ingestion error, GE validation failure, any
#         unhandled exception) - nothing was promoted to the warehouse
#
# The imports below reference functions described (but not yet
# implemented) in the other src/ modules' comments. This file will raise
# ImportError/NotImplementedError until those modules are filled in — that
# is expected, not a bug: build the modules bottom-up, then this entrypoint
# ties them together end to end.

import logging
import sys

from src.config import get_settings
from src.ingestion.s3_reader import load_month
from src.reconciliation.schema_registry import load_all_schema_versions
from src.reconciliation.column_mapper import reconcile
from src.refinement.text_normalization import normalize_column
from src.refinement.deduplication import deduplicate
from src.refinement.outlier_detection import treat_outliers
from src.refinement.consolidation import consolidate_month
from src.quarantine.quarantine_handler import write_to_quarantine

logger = logging.getLogger(__name__)


def run(year_month: str) -> None:
    # Orchestrate one full pipeline run for `year_month`. Suggested steps:
    #
    #   1. ingest      -> load_month(bucket, year_month) for every file
    #                     under that month's MinIO prefix
    #   2. reconcile   -> reconcile(df, year_month, schema_versions) per
    #                     file: rename to canonical columns, coerce dtypes
    #   3. refine      -> normalize_column -> deduplicate ->
    #                     treat_outliers -> consolidate_month (merges the
    #                     month's files into one consolidated DataFrame)
    #   4. validate    -> run the Great Expectations checkpoint against the
    #                     refined output; if checkpoint_result.success is
    #                     False, raise — do NOT proceed to load
    #   5. load        -> write the validated DataFrame to the warehouse
    #                     table (only reached if validation passed)
    #   6. quarantine  -> write_to_quarantine() for any flagged/rejected
    #                     rows collected along the way, with their reasons
    #   7. metrics     -> log quality metrics for this run to MLflow
    #                     (% duplicates found, % corrected, % failed
    #                     validation, row counts in/out)
    #
    # Let any failure propagate as a plain exception - main() below is the
    # only place that translates that into a process exit code.
    raise NotImplementedError("Implement the pipeline steps in run().")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    year_month = settings.year_month  # from YEAR_MONTH env var
    if not year_month:
        logger.error("YEAR_MONTH env var is required")
        sys.exit(1)

    try:
        run(year_month)
    except Exception:
        logger.exception("Pipeline run failed for %s", year_month)
        sys.exit(1)

    logger.info("Pipeline run succeeded for %s", year_month)
    sys.exit(0)


if __name__ == "__main__":
    main()
