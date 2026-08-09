# src/config.py
#
# Centralized runtime configuration. Every module under src/ should read
# settings from here instead of calling os.getenv() ad hoc, so there's a
# single source of truth and a single place to validate that required env
# vars are present at startup. This module (and everything in src/) is
# orchestrator-agnostic — it only ever reads plain environment variables,
# never anything Airflow-specific (no Variables, no Connections, no XComs).
#
# Implement:
#
# - Call load_dotenv() (python-dotenv) at import time so this also works
#   when running scripts locally outside of Docker.
#
# - A Settings object (plain dataclass, or pydantic BaseSettings if you
#   want built-in validation/type coercion) with fields for:
#     * year_month: str          - from YEAR_MONTH, which vendor drop to
#       process this run (read by src/main.py)
#     * MinIO/S3: endpoint_url, access_key, secret_key, bucket_name, region
#     * Postgres warehouse: a SQLAlchemy connection string (or the pieces
#       to build one) -> exposed as a get_warehouse_engine() factory
#     * MLflow: tracking_uri, experiment_name
#     * schema_registry_dir: path to schema_registry/ so
#       src.reconciliation.schema_registry doesn't hardcode it
#
# - get_settings() -> Settings, cached (functools.lru_cache) so it behaves
#   like a singleton within a process, but is still easy to override in
#   tests (e.g. get_settings.cache_clear() + monkeypatched env vars).
#
# Why this matters: ingestion, refinement, quarantine, and src/main.py all
# need the same connection details. Duplicating os.getenv() calls across
# files is exactly how those values silently drift out of sync — ironic,
# given the project is about drift.
