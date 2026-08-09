#!/bin/bash
# Runs automatically on first container boot (mounted into
# /docker-entrypoint-initdb.d/ by docker-compose.yml). Creates one database
# per name listed in POSTGRES_MULTIPLE_DATABASES (comma-separated) so a
# single postgres:15 instance can host warehouse, airflow, and mlflow as
# separate logical databases.
set -e
set -u

function create_database() {
  local database=$1
  echo "Creating database '$database'"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE "$database";
EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
  echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
  for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
    create_database "$db"
  done
  echo "Multiple databases created"
fi
