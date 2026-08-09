# Great Expectations layer

This directory is intentionally mostly empty — Great Expectations scaffolds
most of its own structure (`great_expectations.yml`, `uncommitted/`, etc.)
when you run its init flow:

    great_expectations init

(or build a DataContext programmatically via the Fluent Data Sources API,
depending on the GE version you pin in requirements.txt — this changed
significantly across 0.x releases, check the docs for the version you
install).

## What to implement

- `expectations/` — one expectation suite per canonical table, e.g.
  `refined_vendor_records`. At minimum, encode the business rules the
  README calls out:
    - completeness: required canonical columns are not null
      (`expect_column_values_to_not_be_null`)
    - `revenue >= 0` (`expect_column_values_to_be_between`)
    - valid `transaction_date` range (not before the business existed, not
      in the future)
    - referential integrity if applicable (e.g. a `client_id` should
      reference values seen elsewhere)
    - schema-level: `expect_table_columns_to_match_ordered_list` against
      the canonical schema from
      `src.reconciliation.schema_registry.get_canonical_schema()`, so a
      pipeline bug producing the wrong shape fails loudly here instead of
      corrupting the warehouse.

- `checkpoints/` — a checkpoint that runs the suite(s) above against the
  *refined* output, invoked from the validation step in `src/main.py`.
  `checkpoint_result.success` is exactly the boolean that step uses to
  decide load-to-warehouse vs. quarantine-only-and-fail.

Keep these suites versioned alongside `schema_registry/` — when the
canonical schema changes, the expectation suite needs to change with it.
