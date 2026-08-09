# tests/test_reconciliation.py
#
# Tests for src/reconciliation/.
#
# Cases to cover:
# - resolve_schema_for_month picks the correct SchemaVersion for a given
#   year-month, including boundary months (valid_from/valid_to edges).
# - resolve_schema_for_month raises a clear error when no version covers
#   the requested month (registry gap).
# - apply_column_mapping renames known columns and flags/logs unknown
#   extra columns rather than dropping them silently.
# - coerce_dtypes produces exactly the canonical dtypes declared in the
#   schema version's `dtypes` block.
