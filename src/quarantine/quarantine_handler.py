# src/quarantine/quarantine_handler.py
#
# Persists rejected/flagged records to a separate Postgres quarantine
# table, with the reason for rejection, instead of dropping them silently.
# This is what makes the pipeline debuggable: nothing just vanishes.
#
# Design the quarantine record shape (dataclass, or just a DataFrame
# contract) with at least:
#   - the original row's columns/values (consider a JSONB `payload` column
#     rather than a rigid fixed schema, since rejected rows by definition
#     don't conform to the canonical schema)
#   - source_key: which MinIO object the row came from
#   - year_month
#   - rejection_reason: str — from outlier_detection, GE validation
#     failures, unmapped-schema columns, consolidation conflicts, etc.
#   - rejected_by_stage: str — "refinement" | "great_expectations" | ...
#   - rejected_at: timestamp
#
# Implement:
#
# write_to_quarantine(df: pd.DataFrame, engine: sqlalchemy.Engine, table_name: str = "quarantine") -> None
#   - Append rows into the quarantine table
#     (df.to_sql(table_name, engine, if_exists="append", index=False)).
#     Create the table with an explicit schema/migration rather than
#     letting to_sql infer types on first write, so the column types stay
#     stable across runs.
#
# read_quarantine_summary(engine: sqlalchemy.Engine, year_month: str) -> pd.DataFrame
#   - Aggregate counts by rejection_reason / rejected_by_stage for a given
#     run. Feeds both human review and the MLflow "% failed validations"
#     metric.
