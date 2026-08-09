# tests/test_ingestion.py
#
# Tests for src/ingestion/. Use moto (S3 mocking) or a local MinIO test
# container to avoid hitting real network calls in unit tests.
#
# Cases to cover:
# - detect_file_type correctly identifies .csv/.xlsx/.json by both
#   extension and magic-byte sniffing (test a mislabeled file, e.g. an
#   xlsx saved with a .csv extension).
# - detect_encoding correctly flags a Latin-1-encoded file containing
#   accented characters vs a UTF-8 one.
# - load_month returns one DataFrame per object under the given prefix,
#   and raises a clear, specific error for an empty/nonexistent prefix.
