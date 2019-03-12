#!/bin/bash

set -e
set -eo pipefail

echo "[Running Tests with Coverage]"
pytest --junitxml=test-reports/junit.xml --cov=./ --verbose

echo

echo "[Uploading Coverage]"
codecov
