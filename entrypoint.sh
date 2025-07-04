#!/usr/bin/env bash

set -e
set -o pipefail
set -u

log() {
  echo "$(date +'%Y-%m-%dT%H:%M:%S') [entrypoint] $1"
}

# Wait for PostgreSQL if needed
if [ -n "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-}" ]; then
  log "Waiting for Postgres to be available..."
  /usr/local/bin/wait-for-it.sh db:5432 -t 30
fi

# Initialize Airflow DB
if [ ! -f "${AIRFLOW_HOME:-/app}/airflow.db" ]; then
  log "Initializing Airflow DB..."
  airflow db init
fi

# Create or update admin user
log "Ensuring admin user exists..."
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email ${ALERT_EMAILS:-admin@example.com} \
  --password admin || true

# Run command
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
