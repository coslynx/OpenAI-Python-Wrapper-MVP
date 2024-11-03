#!/bin/bash

set -euo pipefail

# Project root directory
PROJECT_ROOT=/app

# Log file location
LOG_FILE=$PROJECT_ROOT/logs/startup.log

# PID file location
PID_FILE=$PROJECT_ROOT/logs/startup.pid

# Service timeouts (in seconds)
DATABASE_TIMEOUT=30
BACKEND_TIMEOUT=30
FRONTEND_TIMEOUT=30

# Health check intervals (in seconds)
HEALTH_CHECK_INTERVAL=5

# Utility functions
log_info() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") INFO: $@" >> $LOG_FILE
}

log_error() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR: $@" >&2
}

cleanup() {
  if [ -f "$PID_FILE" ]; then
    rm "$PID_FILE"
  fi
  
  # Stop services if needed
}

check_dependencies() {
  # Check for required tools
  command -v docker >/dev/null 2>&1 || { log_error "Docker is required"; exit 1; }
  command -v pip >/dev/null 2>&1 || { log_error "Pip is required"; exit 1; }
  command -v uvicorn >/dev/null 2>&1 || { log_error "Uvicorn is required"; exit 1; }
}

# Health check functions
check_port() {
  nc -z "$1" "$2" >/dev/null 2>&1
}

wait_for_service() {
  local service_name=$1
  local port=$2
  local timeout=$3
  local elapsed=0

  while [[ $elapsed -lt $timeout ]]; do
    log_info "Waiting for $service_name on port $port..."
    if check_port "$1" "$2"; then
      log_info "$service_name is up!"
      return 0
    fi
    sleep $HEALTH_CHECK_INTERVAL
    ((elapsed+=HEALTH_CHECK_INTERVAL))
  done

  log_error "$service_name failed to start within $timeout seconds."
  exit 1
}

verify_service() {
  local service_name=$1
  local endpoint=$2
  local timeout=$3

  local elapsed=0
  while [[ $elapsed -lt $timeout ]]; do
    log_info "Verifying $service_name health..."
    curl -s -o /dev/null -w "%{http_code}" "$endpoint" >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
      log_info "$service_name is healthy!"
      return 0
    fi
    sleep $HEALTH_CHECK_INTERVAL
    ((elapsed+=HEALTH_CHECK_INTERVAL))
  done

  log_error "$service_name is not healthy."
  exit 1
}

# Service management functions
start_database() {
  # Start PostgreSQL
  pg_ctl -D /var/lib/postgresql/data start
  wait_for_service "PostgreSQL" "$POSTGRES_PORT" "$DATABASE_TIMEOUT"
}

start_backend() {
  # Start FastAPI server
  uvicorn main:app --host 0.0.0.0 --port $PORT --reload &
  wait_for_service "Backend" "$PORT" "$BACKEND_TIMEOUT"
  verify_service "Backend" "http://localhost:$PORT/api/v1/health" "$BACKEND_TIMEOUT"
}

start_frontend() {
  # Start frontend service (if applicable)
  # ...
  wait_for_service "Frontend" "$FRONTEND_PORT" "$FRONTEND_TIMEOUT"
  verify_service "Frontend" "http://localhost:$FRONTEND_PORT" "$FRONTEND_TIMEOUT"
}

store_pid() {
  # Store process IDs for cleanup
  echo $$ > "$PID_FILE"
}

# Main execution flow
trap cleanup EXIT ERR

log_info "Starting services..."

# Load environment variables
source $PROJECT_ROOT/.env
export OPENAI_API_KEY=$OPENAI_API_KEY
export POSTGRES_HOST=$POSTGRES_HOST
export POSTGRES_PORT=$POSTGRES_PORT
export POSTGRES_USER=$POSTGRES_USER
export POSTGRES_PASSWORD=$POSTGRES_PASSWORD
export POSTGRES_DATABASE=$POSTGRES_DATABASE

# Install Python dependencies
pip install -r $PROJECT_ROOT/requirements.txt

# Start services
start_database
start_backend
start_frontend

log_info "Services started successfully!"
store_pid