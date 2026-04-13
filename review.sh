#!/bin/bash
# fintrdr Morning Review Shortcut

echo "--- Starting fintrdr Morning Review ---"
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:.
uv run python src/application/real_time_advisor.py
echo "--- Review Complete ---"
