#!/usr/bin/env bash

set -euo pipefail

log() {
  echo "$(date +'%Y-%m-%dT%H:%M:%S') [entrypoint] $1"
}

# Wait for Postgres to be available if connection string is set
if [ -n "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-}" ]; then
  log "Waiting for Postgres to be available..."
  /usr/local/bin/wait-for-it.sh db:5432 -t 30
fi

# Initialize Airflow DB if it does not exist
if [ ! -f "${AIRFLOW_HOME:-/app}/airflow.db" ]; then
  log "Initializing Airflow DB..."
  airflow db init
fi

# Create or update admin user (idempotent)
log "Ensuring admin user exists..."
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email "${ALERT_EMAILS:-admin@example.com}" \
  --password admin || true

# Run passed command
case "$1" in
  webserver)
    log "Starting Airflow Webserver..."
    exec airflow webserver
    ;;
  scheduler)
    log "Starting Airflow Scheduler..."
    exec airflow scheduler
    ;;
  *)
    log "Running custom command: $*"
    exec "$@"
    ;;
esac
