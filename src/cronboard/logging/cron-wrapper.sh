#!/bin/bash

set -o pipefail

LOG_DIR="${CRONBOARD_LOG_DIR:-$HOME/.cronboard/logs}"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
JOB_NAME="${1:-unknown_job}"
shift

LOG_FILE="$LOG_DIR/${JOB_NAME}_${TIMESTAMP}.log"
ERR_FILE="$LOG_DIR/${JOB_NAME}_${TIMESTAMP}.err"

# Ensure PATH works in cron
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Header
{
  echo "========================================"
  echo "Cronboard Job Execution"
  echo "Job: $JOB_NAME"
  echo "Time: $TIMESTAMP"
  echo "Command: $*"
  echo "========================================"
  echo ""
} > "$LOG_FILE"

# Run command (capture stdout + stderr separately for stable ordering)
"$@" > "$LOG_FILE.out" 2> "$ERR_FILE"
EXIT_CODE=$?

# Append stdout first
if [ -s "$LOG_FILE.out" ]; then
  cat "$LOG_FILE.out" >> "$LOG_FILE"
fi

# Append cleaned stderr after stdout (stable order)
if [ -s "$ERR_FILE" ]; then
  echo "" >> "$LOG_FILE"
  sed 's/^.*: line [0-9]\+: //' "$ERR_FILE" >> "$LOG_FILE"
fi

# Footer
{
  echo ""
  echo "========================================"
  echo "Exit Code: $EXIT_CODE"
  echo "Status: $([ $EXIT_CODE -eq 0 ] && echo SUCCESS || echo FAILED)"
  echo "========================================"
} >> "$LOG_FILE"

# Cleanup temp files
rm -f "$LOG_FILE.out" "$ERR_FILE"

exit $EXIT_CODE