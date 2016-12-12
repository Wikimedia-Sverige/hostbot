#! /usr/bin/env bash

start_time=$(date "+%F:%T")
log_path=logs/$start_time.log
# Go to the hostbot directory
cd "$(dirname "$0")"/.. || exit
/usr/bin/time -f "Execution time: %E" -ao "$log_path" venv_invite/bin/python scripts/teahouse/send_th_invites.py > "$log_path" 2>&1
