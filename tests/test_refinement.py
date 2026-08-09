# tests/test_refinement.py
#
# Tests for src/refinement/ — the core logic of the project, so give it the
# most coverage.
#
# Cases to cover:
# - normalize_categorical collapses "Bogotá" / "BOGOTA" / "bogota d.c." to
#   the same normalized value.
# - deduplicate() clusters near-identical entity names above the
#   similarity threshold and leaves genuinely distinct names apart (test
#   both a true-positive merge and a true-negative non-merge).
# - parse_mixed_dates correctly parses an ISO date, a DD/MM/YYYY date, and
#   an Excel serial number to the same underlying date.
# - detect_outliers_iqr / detect_outliers_zscore flag known synthetic
#   outliers and do not flag normal values.
# - resolve_conflicts picks the documented winner when two files disagree
#   on a field for the same entity.
