# src/refinement/deduplication.py
#
# Fuzzy deduplication of entities using rapidfuzz similarity scoring — the
# "near-identical but non-identical names" problem, not exact-match dedup
# (pandas .drop_duplicates() alone can't solve this).
#
# Implement:
#
# find_candidate_pairs(df: pd.DataFrame, key_column: str, threshold: float = 90.0) -> list[tuple[int, int, float]]
#   - Run on the *normalized* key_column (use
#     src.refinement.text_normalization first). Score pairs with
#     rapidfuzz.fuzz.token_sort_ratio or WRatio.
#   - All-pairs comparison is O(n^2) — for a realistic dataset size,
#     implement blocking first (e.g. group by first letter, or a phonetic
#     key like soundex/metaphone) to cut candidate pairs down before
#     scoring the expensive way. rapidfuzz.process.cdist can also help
#     vectorize the scoring step within a block.
#
# build_duplicate_clusters(pairs: list[tuple[int, int, float]]) -> list[set[int]]
#   - Union-find (or networkx connected components) over pairs above
#     threshold, so A~B and B~C implies {A, B, C} is one entity even
#     though A~C was never directly compared.
#
# choose_canonical_record(cluster_df: pd.DataFrame) -> pd.Series
#   - Business rule for which record "wins" per cluster (e.g. most
#     complete row, most recent, longest/most-punctuated name as the
#     presumed "full" form). Document the rule you pick.
#
# deduplicate(df: pd.DataFrame, key_column: str, threshold: float = 90.0) -> tuple[pd.DataFrame, pd.DataFrame]
#   - Orchestrates the above; returns (deduplicated_df, dedup_report_df).
#     The report (clusters found, records collapsed per cluster) feeds the
#     MLflow "% duplicates found" metric mentioned in the README.
