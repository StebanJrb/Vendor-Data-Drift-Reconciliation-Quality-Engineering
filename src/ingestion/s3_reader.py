# src/ingestion/s3_reader.py
#
# boto3-based reader for the MinIO "raw/vendor-drops/YYYY-MM/" prefix. This
# is the ingestion boundary: nothing downstream should read local files
# directly — everything comes through here, mirroring how you'd read from
# real S3 in production.
#
# Implement:
#
# get_s3_client() -> boto3.client
#   - Build the client from src.config settings (endpoint_url pointed at
#     MinIO, access/secret key, region). Keep this the single place that
#     constructs the client.
#
# list_objects_for_month(bucket: str, year_month: str) -> list[str]
#   - List every object key under raw/vendor-drops/{year_month}/
#     (paginate with list_objects_v2 if you expect >1000 keys, otherwise a
#     single call is fine at this scale).
#
# read_object(bucket: str, key: str) -> bytes
#   - GetObject, return raw bytes. Hand off to
#     src.ingestion.file_detector for type/encoding handling — this
#     function should know nothing about file formats.
#
# load_month(bucket: str, year_month: str) -> list[tuple[str, pd.DataFrame]]
#   - Orchestrates list_objects_for_month + read_object + file_detector to
#     return every file in that month's drop as a (source_key, DataFrame)
#     pair. This is what src.reconciliation and the ingest step in
#     src/main.py actually call.
#
# Things to get right:
#   - Don't assume exactly one file per month — the README explicitly
#     calls out "same entity reported differently across two files landing
#     the same month", so load_month must support >1 file per prefix.
#   - Raise a clear, specific error (not a bare pandas stack trace) when a
#     requested month's prefix has zero objects.
