# src/refinement/outlier_detection.py
#
# Outlier detection and treatment (IQR/z-score) on numeric fields, with
# documented business rules for what gets flagged vs. corrected vs. dropped.
#
# Implement:
#
# detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series[bool]
#   - Standard Q1/Q3 +/- k*IQR boolean mask.
#
# detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series[bool]
#   - abs(z-score) > threshold boolean mask. Useful as a second signal, or
#     for columns where IQR is too aggressive on skewed data.
#
# classify_outlier_action(row: pd.Series, column: str, context: dict) -> Literal["flag", "correct", "drop"]
#   - This is the "documented business rules" part the README calls out —
#     decide and write down the rules, e.g.:
#       * negative revenue on an otherwise valid row -> correct (abs()) or
#         quarantine, never silently drop
#       * a revenue value ~1000x the column median with no other anomaly
#         -> flag for manual review
#       * clearly impossible values (e.g. transaction_date in the future)
#         -> drop / route straight to quarantine
#
# treat_outliers(df: pd.DataFrame, numeric_columns: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]
#   - Returns (clean_df, flagged_df), where flagged_df carries a
#     `rejection_reason` column. flagged_df is what src.quarantine
#     persists.
