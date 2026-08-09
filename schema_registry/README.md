# Schema Registry

YAML-driven column mapping + dtype contract, one file per historical vendor
export "shape" (`vendor_schema_v1.yml` .. `vendor_schema_v6.yml`). This is
what `src/reconciliation/schema_registry.py` loads and resolves against a
given year-month before `src/reconciliation/column_mapper.py` applies it.

See `vendor_schema_v1.yml` for the expected file shape.

As you build `src/generator/drift_generator.py` and decide which mutation
happens in which month, add a corresponding `vendor_schema_vN.yml` here
with matching `valid_from`/`valid_to` bounds — the generator and the
registry must describe the same drift timeline, or reconciliation will
silently mismatch columns.

You don't need exactly 6 versions — the README's v1..v6 naming is
illustrative. Add one version per genuine schema-shape change your
generator introduces.
