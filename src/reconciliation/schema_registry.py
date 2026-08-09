# src/reconciliation/schema_registry.py
#
# Loads and queries the version-aware schema registry
# (schema_registry/vendor_schema_v1..v6.yml). Each YAML file describes one
# historical vendor export shape: which raw column names map to canonical
# column names, and what dtype each canonical column should be coerced to.
# See schema_registry/vendor_schema_v1.yml for the expected YAML shape.
#
# Implement:
#
# A SchemaVersion dataclass:
#   version: int
#   valid_from: str          # "YYYY-MM"
#   valid_to: str | None      # "YYYY-MM", inclusive, or None if open-ended
#   column_mapping: dict[str, str]   # raw_column -> canonical_column
#   dtypes: dict[str, str]           # canonical_column -> dtype token
#   date_format: str | None          # strftime pattern, or "excel_serial"
#
# load_all_schema_versions(registry_dir: str) -> list[SchemaVersion]
#   - Parse every vendor_schema_v*.yml in registry_dir into SchemaVersion
#     objects. Fail loudly (don't skip) on a malformed YAML file — a bad
#     registry entry should never silently disappear.
#
# resolve_schema_for_month(year_month: str, versions: list[SchemaVersion]) -> SchemaVersion
#   - Find the version whose [valid_from, valid_to] range covers
#     year_month. Raise a clear, specific error if none match (that's a
#     registry gap, not something to silently fall back on) and if more
#     than one match (overlapping ranges are a registry bug).
#
# get_canonical_schema(versions: list[SchemaVersion]) -> dict[str, str]
#   - The final unified canonical_column -> dtype mapping every version
#     ultimately reconciles into (should be identical across all versions'
#     `dtypes` — assert that, since divergence here is itself a bug worth
#     catching). This is the contract src.refinement and the Great
#     Expectations suite are both written against.
