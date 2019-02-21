#!/bin/bash

set -e
set -eo pipefail


conda config --set always_yes true --set quiet true
conda update conda
conda config --add channels conda-forge
conda env create -f .circleci/${ENV_SCRIPT} --name ${ENV_NAME}
conda env list
source activate ${ENV_NAME}
conda list -n ${ENV_NAME}