# src/generator/drift_generator.py
#
# Synthetic "vendor drift" generator. Takes one clean source dataset (e.g.
# SECOP II from datos.gov.co, or the Olist Brazilian e-commerce dataset)
# and re-exports it as 18-24 monthly snapshots that simulate a vendor's
# export format silently changing over time. This is what makes the whole
# project reproducible for anyone cloning the repo, instead of depending on
# hand-curated fixture files.
#
# Implement:
#
# 1. load_source_dataset(path: str) -> pd.DataFrame
#    - Read the base "clean" dataset once.
#
# 2. A small registry of drift "mutations", each shaped like
#    (df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
#      - rename_columns(df, mapping)                  # customer_name -> client_name -> nombre_cliente
#      - shift_date_format(df, column, fmt)            # ISO -> DD/MM/YYYY -> Excel serial
#      - inject_encoding_issues(df, column)             # re-encode as latin-1 to mangle accents
#      - randomize_categorical_casing(df, column)       # "Bogota" / "BOGOTA" / "bogota d.c."
#      - inject_fuzzy_duplicates(df, key_column, rate)  # near-identical entity names
#      - drop_or_add_columns(df, add=[], drop=[])       # simulate deprecated/new fields
#      - inject_missing_values(df, columns, rate)
#      - inject_outliers(df, numeric_columns, rate)
#
# 3. build_monthly_snapshots(df, n_months=24, seed=42) -> dict[str, pd.DataFrame]
#    - For each month (YYYY-MM), pick a schema "version" (an explicit
#      MONTH_TO_SCHEMA_VERSION mapping) and apply that version's mutations
#      in sequence. Keep this mapping documented so schema_registry/
#      vendor_schema_v*.yml can describe exactly what changed and when —
#      the generator and the registry must agree on the same timeline.
#
# 4. export_snapshot(df, month, file_format) -> bytes | local path
#    - Support at least CSV, XLSX (openpyxl), and JSON, matching the
#      "some files are CSV, some are Excel, some are JSON" premise from the
#      README.
#
# 5. upload_to_minio(local_path_or_bytes, bucket, key) using boto3 (via
#    src.config for credentials), landing files under
#    raw/vendor-drops/YYYY-MM/<filename>.
#
# 6. A CLI entrypoint:
#      if __name__ == "__main__": ...
#    so this can be run as `python -m src.generator.drift_generator` to
#    (re)populate MinIO from scratch.
#
# Determinism matters: seed every random choice so the generated drift is
# reproducible run to run. Document each schema version's changes as you
# build them (see schema_registry/README.md).
