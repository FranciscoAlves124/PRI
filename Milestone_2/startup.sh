#!/bin/bash

set -euo pipefail

# ===== Terminal / run notes =====
# Linux / macOS (bash, sh)
#  - Make executable (optional): chmod +x startup.sh
#  - Run: ./startup.sh basic
#  - Or run without +x: bash startup.sh basic
#  - If you need sudo for Docker commands: sudo bash startup.sh basic
#
# Windows / PowerShell
#  - This is a bash script. Use WSL, Git Bash, or run from a Linux/Mac shell.
#  - Example using WSL from PowerShell: wsl bash ./startup.sh basic
#  - Alternatively create a PowerShell equivalent (startup.ps1) or use Docker Compose.
#
# Common issues
#  - "Permission denied": use chmod +x or run with `bash startup.sh`.
#  - "sudo: ./startup.sh: command not found": use `sudo bash startup.sh` (sudo doesn't search ./).
#  - If filesystem is mounted with noexec: run `bash startup.sh` or move script to exec-enabled path.
#  - Modes: basic (schemaless), intermediate (custom schema), both.
#  - Usage: ./startup.sh [basic|intermediate|both]
# ===== end run notes =====

# default to basic (schemaless) when no arg provided
MODE="${1:-basic}"   # usage: ./startup.sh [basic|intermediate|both]
# pass --recreate to force core recreation: ./startup.sh intermediate --recreate
RECREATE=false
if [ "${2:-}" = "--recreate" ]; then RECREATE=true; fi

PWD_DIR="$(pwd)"
CONTAINER_NAME="initial_solr"
HOST_PORT=8983
DATA_PATH="/data/final_data_solr/movies_series.json"

echo "mode=$MODE  recreate=$RECREATE"

# accept "schemaless" as alias for "basic"
if [ "$MODE" = "schemaless" ]; then
  MODE="basic"
fi

# ensure docker available
if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found" >&2
  exit 1
fi

# start container if missing
if [ -z "$(docker ps -a --filter "name=${CONTAINER_NAME}" --format '{{.Names}}')" ]; then
  docker pull solr:9
  docker run -d -p ${HOST_PORT}:8983 --name ${CONTAINER_NAME} -v "${PWD_DIR}:/data" solr:9
else
  docker start ${CONTAINER_NAME} >/dev/null || true
fi

# wait for Solr to respond
until curl -sSf "http://localhost:${HOST_PORT}/solr/" >/dev/null 2>&1; do
  printf "."
  sleep 1
done
echo
echo "Solr ready"

# helper: check if core exists and has a conf dir
core_exists() {
  local core="$1"
  # check core presence via cores API
  if ! curl -s "http://localhost:${HOST_PORT}/solr/admin/cores?action=STATUS&core=${core}&wt=json" | grep -q "\"${core}\""; then
    return 1
  fi
  # ensure conf dir exists inside container; if missing treat as non-existent so we recreate
  if ! docker exec "${CONTAINER_NAME}" test -d "/var/solr/data/${core}/conf" >/dev/null 2>&1; then
    echo "core ${core} present but conf dir missing; will recreate" >&2
    return 1
  fi
  return 0
}

# helper: create core idempotently
create_core() {
  local core="$1"
  local configset="$2"
  if core_exists "${core}"; then
    echo "core ${core} already exists and has conf"
  else
    echo "creating core ${core} (-n ${configset})"
    docker exec "${CONTAINER_NAME}" solr create -c "${core}" -n "${configset}"
  fi
}

# helper: delete core if present
delete_core() {
  local core="$1"
  if core_exists "${core}"; then
    echo "deleting core ${core}"
    docker exec "${CONTAINER_NAME}" solr delete -c "${core}"
    # give Solr a moment to settle
    sleep 1
  fi
}

# prepare schema payload (convert add-* to replace-* so re-running is safe)
prepare_schema_for_replace() {
  local in="$1"; local out="$2"
  sed -e 's/"add-field"/"replace-field"/g' \
      -e 's/"add-field-type"/"replace-field-type"/g' \
      "$in" > "$out"
}

# create/apply/index depending on mode
case "$MODE" in
  basic)
    # schemaless behaviour (data_driven_schema_configs)
    if [ "$RECREATE" = true ]; then delete_core media_basic; fi
    create_core media_basic data_driven_schema_configs
    echo "Indexing data into media_basic..."
    docker exec "${CONTAINER_NAME}" solr post -c media_basic "${DATA_PATH}"
    ;;
  intermediate)
    if [ "$RECREATE" = true ]; then delete_core media_intermediate; fi
    create_core media_intermediate basic_configs
    if [ -f "./intermediate_schema.json" ]; then
      TMP_SCHEMA="$(mktemp)"
      prepare_schema_for_replace "./intermediate_schema.json" "${TMP_SCHEMA}"
      echo "Applying intermediate schema to media_intermediate..."
      RESP="$(curl -s -w "%{http_code}" -X POST -H 'Content-type:application/json' --data-binary "@${TMP_SCHEMA}" "http://localhost:${HOST_PORT}/solr/media_intermediate/schema")"
      HTTP="${RESP: -3}"
      BODY="${RESP::-3}"
      echo "Schema API HTTP=$HTTP"
      echo "$BODY" | sed -n '1,200p'
      if [ "$HTTP" -ge 300 ]; then
        echo "Schema apply failed (HTTP $HTTP). Aborting." >&2
        rm -f "${TMP_SCHEMA}"
        exit 1
      fi
      rm -f "${TMP_SCHEMA}"
    else
      echo "intermediate_schema.json not found, skipping schema apply"
    fi
    echo "Indexing data into media_intermediate..."
    docker exec "${CONTAINER_NAME}" solr post -c media_intermediate "${DATA_PATH}"
    ;;
  both)
    if [ "$RECREATE" = true ]; then delete_core media_basic; delete_core media_intermediate; fi
    create_core media_basic data_driven_schema_configs
    create_core media_intermediate basic_configs
    if [ -f "./intermediate_schema.json" ]; then
      TMP_SCHEMA="$(mktemp)"
      prepare_schema_for_replace "./intermediate_schema.json" "${TMP_SCHEMA}"
      echo "Applying intermediate schema to media_intermediate..."
      RESP="$(curl -s -w "%{http_code}" -X POST -H 'Content-type:application/json' --data-binary "@${TMP_SCHEMA}" "http://localhost:${HOST_PORT}/solr/media_intermediate/schema")"
      HTTP="${RESP: -3}"
      BODY="${RESP::-3}"
      echo "Schema API HTTP=$HTTP"
      echo "$BODY" | sed -n '1,200p'
      if [ "$HTTP" -ge 300 ]; then
        echo "Schema apply failed (HTTP $HTTP). Aborting." >&2
        rm -f "${TMP_SCHEMA}"
        exit 1
      fi
      rm -f "${TMP_SCHEMA}"
    fi
    echo "Indexing data into both cores..."
    docker exec "${CONTAINER_NAME}" solr post -c media_basic "${DATA_PATH}"
    docker exec "${CONTAINER_NAME}" solr post -c media_intermediate "${DATA_PATH}"
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Usage: $0 [basic|intermediate|both] [--recreate]"
    exit 2
    ;;
esac

echo "Done."