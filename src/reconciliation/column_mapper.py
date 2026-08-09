# src/reconciliation/column_mapper.py
#
# Applies a resolved SchemaVersion (from schema_registry.py) to an ingested
# DataFrame: renames vendor-specific columns to canonical names and coerces
# dtypes, so everything downstream in src.refinement operates on one
# consistent shape regardless of which month/version it came from.
#
# Implement:
#
# apply_column_mapping(df: pd.DataFrame, schema: SchemaVersion) -> pd.DataFrame
#   - df.rename(columns=schema.column_mapping), but be defensive:
#     * log/flag any raw columns present in df that aren't in the mapping
#       (unknown columns the registry doesn't know about yet) instead of
#       silently dropping them
#     * log/flag any canonical columns the mapping expects that are
#       missing from df (deprecated/absent that month)
#
# coerce_dtypes(df: pd.DataFrame, schema: SchemaVersion) -> pd.DataFrame
#   - For each canonical column, cast to schema.dtypes[column]. Delegate
#     the actual parsing logic (mixed date formats, Excel serial dates,
#     numeric cleanup) to src.refinement.type_coercion rather than
#     duplicating it here — this function should just orchestrate.
#
# reconcile(df: pd.DataFrame, year_month: str, versions: list[SchemaVersion]) -> pd.DataFrame
#   - Convenience wrapper: resolve_schema_for_month + apply_column_mapping
#     + coerce_dtypes in one call. This is what the ingestion loop / DAG
#     task actually calls per file.
