#! /usr/bin/env bash

start_time=$(date "+%F_%T")
log_path=logs/$start_time.log
# Go to the hostbot directory
cd "$(dirname "$0")"/.. || exit
/usr/bin/time -f "Execution time: %E" -ao "$log_path" venv_invite/bin/python scripts/teahouse/send_th_invites.py -l "$log_path"
