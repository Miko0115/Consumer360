#!/bin/bash
PROJECT_DIR="/run/media/miko/Autumn/Consumer360 Project"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"
~/miniconda3/envs/ml/bin/python Consumer360.py >> "$LOG_DIR/pipeline.log" 2>&1
echo "Exit code: $?" >> "$LOG_DIR/pipeline.log"
echo "---RUN COMPLETE: $(date)---" >> "$LOG_DIR/pipeline.log"
