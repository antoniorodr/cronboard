#!/bin/bash

LOG_DIR="${CRONBOARD_LOG_DIR:-$HOME/.cronboard/logs}"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
JOB_NAME="${1:-unknown_job}"
shift

LOG_FILE="$LOG_DIR/${JOB_NAME}_${TIMESTAMP}.log"

{
  echo "========================================"
  echo "Cronboard Job Execution"
  echo "Job: $JOB_NAME"
  echo "Time: $TIMESTAMP"
  echo "Command: $*"
  echo "========================================"
  echo ""
} > "$LOG_FILE"

"$@" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

{
  echo ""
  echo "========================================"
  echo "Exit Code: $EXIT_CODE"
  echo "Status: $([ $EXIT_CODE -eq 0 ] && echo SUCCESS || echo FAILED)"
  echo "========================================"
} >> "$LOG_FILE"

exit $EXIT_CODE