# src/refinement/consolidation.py
#
# Multi-file consolidation with conflict resolution: the same entity
# reported differently across two files landing in the same month's drop.
#
# Implement:
#
# merge_month_files(dfs: list[pd.DataFrame], key_column: str) -> pd.DataFrame
#   - Concatenate the month's already-reconciled/normalized/deduplicated
#     files, then group by the (deduplicated) entity key.
#
# resolve_conflicts(group: pd.DataFrame) -> pd.Series
#   - Per-entity conflict resolution for columns that disagree across
#     files. Document the rule you choose, e.g.:
#       * most-recently-modified file wins
#       * non-null wins over null
#       * numeric values disagreeing by more than X% get flagged instead
#         of silently picking one
#     This is a business decision, not a technical one — write it down
#     once you decide, and keep resolve_conflicts matching that decision.
#
# consolidate_month(dfs: list[pd.DataFrame], key_column: str) -> tuple[pd.DataFrame, pd.DataFrame]
#   - Orchestrates merge_month_files + resolve_conflicts; returns
#     (consolidated_df, conflicts_report_df). conflicts_report_df feeds
#     both src.quarantine and an MLflow metric ("% records requiring
#     correction").
