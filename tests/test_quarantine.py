# tests/test_quarantine.py
#
# Tests for src/quarantine/. Use a throwaway/test Postgres schema (or
# sqlite in-memory, if your quarantine table design is portable enough)
# rather than the real warehouse DB.
#
# Cases to cover:
# - write_to_quarantine persists all expected columns, including
#   rejection_reason and source metadata (source_key, year_month,
#   rejected_by_stage).
# - read_quarantine_summary correctly aggregates counts by
#   rejection_reason / rejected_by_stage for a given year_month.
