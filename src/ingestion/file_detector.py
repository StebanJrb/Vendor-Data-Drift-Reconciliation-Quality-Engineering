# src/ingestion/file_detector.py
#
# Detects file type and text encoding for a raw vendor file before it's
# parsed, since a single month's drop can mix CSV/XLSX/JSON, and CSV files
# can be UTF-8 or Latin-1.
#
# Implement:
#
# detect_file_type(filename: str, content: bytes) -> Literal["csv", "xlsx", "json"]
#   - Prefer the extension first, but don't trust it blindly: sniff magic
#     bytes as a fallback for mislabeled files (XLSX is a zip archive and
#     starts with b"PK"; JSON should parse cleanly via json.loads).
#
# detect_encoding(content: bytes) -> str
#   - Use charset-normalizer (from_bytes(content).best()) to guess encoding
#     for CSV/text files. Return a sane default ("utf-8") above some
#     confidence threshold, and fall back to "latin-1" below it — that's
#     the specific failure mode called out in the README.
#
# read_raw_bytes_as_dataframe(content: bytes, file_type: str, encoding: str) -> pd.DataFrame
#   - Dispatch to pd.read_csv / pd.read_excel / pd.read_json with the
#     detected type + encoding. Centralize this so ingestion callers never
#     need to know the parsing details themselves.
#
# Edge cases to handle deliberately (log, don't silently swallow):
#   - Low-confidence encoding detection -> proceed but tag the file for
#     downstream review instead of guessing silently.
#   - Excel files with multiple sheets -> decide and document which sheet
#     you read (first sheet only, or a configured sheet name).
