# Vendor Data Drift Reconciliation & Quality Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Great Expectations](https://img.shields.io/badge/Great%20Expectations-FF6F00?style=flat&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=apacheairflow&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat&logo=mlflow&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat&logo=minio&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Overview

A pipeline that ingests messy, schema-drifted data extracts landing in object storage (simulating vendor/partner data drops over time), reconciles them into a unified schema using advanced Pandas transformations, and enforces data contracts with Great Expectations before promoting the data to a PostgreSQL warehouse. This is the real-world problem every Data Engineer eventually hits: the source data almost never arrives clean, and it rarely arrives in the same shape twice.

## The Problem

A retail/logistics company receives monthly data extracts from an external vendor system (contracts, transactions, or shipment records). Over a 24-month period, the vendor's export format silently changed multiple times:

- Column names were renamed (`customer_name` → `client_name` → `nombre_cliente`)
- New columns were added mid-year, others deprecated
- Date formats shifted (`YYYY-MM-DD` → `DD/MM/YYYY` → Excel serial dates)
- Encoding inconsistencies (UTF-8 vs Latin-1, producing broken accented characters)
- Categorical values are inconsistent (`"Bogotá"`, `"BOGOTA"`, `"bogota d.c."`, `"Bogota D.C."`)
- Duplicate entities exist under near-identical but non-identical names (fuzzy duplicates, not exact ones)
- Some files are CSV, some are Excel, some are JSON exports from a different system version

None of this is contrived for difficulty — this is the standard failure mode of any pipeline that depends on an external, loosely-governed data source. The job of this project is to make that chaos production-safe.

## Data Source

**Recommended approach — hybrid (realistic + reproducible):**

1. Start from a real base dataset with genuine business semantics — e.g. **SECOP II** (Colombian public procurement, available at [datos.gov.co](https://www.datos.gov.co)) or the **Brazilian E-Commerce Public Dataset (Olist)** on Kaggle.
2. Run a small synthetic "drift generator" script (included in `src/generator/`) that takes clean source data and re-exports it as 18–24 monthly snapshots, deliberately introducing the drift patterns above (renamed columns, format shifts, injected duplicates/typos, encoding issues) in a controlled, documented way.
3. Land these files in **MinIO** (S3-compatible, running locally via Docker) under a `raw/vendor-drops/YYYY-MM/` prefix — this is what you'll read from using `boto3`, exactly as you would against real AWS S3.

This gives you a dataset that is both realistic in its problem shape and fully reproducible for anyone reviewing your repo.

## Architecture

- **Ingestion:** `boto3` reads all files under a given month's prefix from MinIO/S3, detecting file type (CSV/XLSX/JSON) and encoding automatically.
- **Schema Reconciliation:** A version-aware schema registry (YAML-driven column mapping) normalizes column names and dtypes across all 24 historical schema versions into one canonical schema — implemented entirely in Pandas.
- **Refinement (the core of the project):**
  - Text normalization: accent stripping, case folding, whitespace/regex cleanup
  - Fuzzy deduplication of entities using `rapidfuzz` similarity scoring, not exact match
  - Type coercion across mixed date formats, including Excel serial date conversion
  - Outlier detection and treatment (IQR/z-score) on numeric fields, with documented business rules for what gets flagged vs. corrected vs. dropped
  - Multi-file consolidation with conflict resolution (e.g. same entity reported differently across two files landing the same month)
- **Validation:** Great Expectations suites run against the *refined* output — completeness, referential integrity, business-rule expectations (e.g. `revenue >= 0`, valid date ranges) — acting as the data contract before promotion.
- **Orchestration:** Airflow DAG with the refinement step gating the load step — if GE validation fails, the run stops and the warehouse table is not updated.
- **Storage:** Refined, validated data lands in PostgreSQL as the "trusted" table; rejected/flagged records are quarantined in a separate table with the reason for rejection.
- **Observability:** Data quality metrics (% duplicates found, % records requiring correction, % failed validations) are logged to MLflow as artifacts per run, so quality trends are trackable over time — not just pass/fail.

## Tech Stack

- Python 3.11+, **Pandas** (core transformation engine), `rapidfuzz` (fuzzy matching)
- `boto3` + MinIO (S3-compatible object storage)
- Great Expectations (data contracts/validation layer)
- PostgreSQL 15 (trusted warehouse + quarantine tables)
- Apache Airflow 2.x (orchestration, quality gate)
- MLflow (quality metrics as artifacts over time)
- Docker & Docker Compose

## What This Demonstrates

- Deep, non-trivial Pandas usage: schema reconciliation across drifted versions, fuzzy deduplication, custom outlier logic, multi-source conflict resolution — not just `read_csv` + `groupby`
- Reading from object storage (S3-compatible) rather than a static local file, mirroring a real ingestion boundary
- Data quality treated as a first-class, measurable, trackable engineering concern rather than a one-off check
- Separation of concerns: Pandas owns *refinement*, Great Expectations owns *contract enforcement*, Airflow owns *gating*
- Designed for a realistic Jr–Mid Data Engineer scope: complex enough to show real skill, scoped enough to actually finish

## Status
🚧 In Development

## Project Structure
```
├── dags/
│   └── vendor_reconciliation_dag.py
├── src/
│   ├── generator/          # synthetic drift generator (creates the 24 monthly drops)
│   ├── ingestion/          # boto3 readers, file-type/encoding detection
│   ├── reconciliation/     # schema registry + column mapping logic
│   ├── refinement/         # dedup, outlier handling, type coercion (core Pandas logic)
│   └── quarantine/
├── great_expectations/
│   ├── expectations/
│   └── checkpoints/
├── schema_registry/
│   └── vendor_schema_v1..v6.yml
├── tests/
├── docker-compose.yml
└── README.md
```
