#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=src

python -m aegisap.day2.run_workflow clean_path --known-vendor
python -m aegisap.day2.run_workflow high_value --known-vendor
python -m aegisap.day2.run_workflow new_vendor
