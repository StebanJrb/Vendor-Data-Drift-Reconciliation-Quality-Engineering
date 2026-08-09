# src/refinement/type_coercion.py
#
# Type coercion across mixed date formats and other dtype mismatches
# introduced by schema drift, including Excel serial date conversion.
#
# Implement:
#
# parse_mixed_dates(series: pd.Series, known_format: str | None = None) -> pd.Series
#   - If known_format == "excel_serial": convert numeric day-counts using
#     pandas' Excel epoch convention:
#       pd.to_datetime(series, unit="D", origin="1899-12-30")
#   - elif known_format is a strftime pattern:
#       pd.to_datetime(series, format=known_format, errors="coerce")
#   - else (format unknown/mixed within the same column): try a small
#     ordered list of candidate formats and take the first that parses a
#     majority of non-null values. Log/count rows that still fail to parse
#     instead of silently turning them into NaT.
#
# coerce_numeric(series: pd.Series) -> pd.Series
#   - Strip thousands separators / currency symbols before
#     pd.to_numeric(series, errors="coerce"); track how many values failed
#     to coerce so it can be surfaced in a quality metric.
#
# coerce_column(df: pd.DataFrame, column: str, target_dtype: str, **kwargs) -> pd.DataFrame
#   - Dispatch to the right coercion function based on target_dtype
#     ("date" -> parse_mixed_dates, "float"/"int" -> coerce_numeric, else
#     plain astype). Called from
#     src.reconciliation.column_mapper.coerce_dtypes.
