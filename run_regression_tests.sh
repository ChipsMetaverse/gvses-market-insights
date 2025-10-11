#!/bin/bash
# Load environment variables and run regression tests
cd "$(dirname "$0")"
set -a
source backend/.env
set +a
python3 test_regression_suite.py