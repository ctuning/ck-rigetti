#!/bin/bash

# This driver script should only be run within CK's virtual environment
# (with or without the python test parameter), like so:
#
#   echo $HOME/CK/ck-rigetti/t/ck_pyquil_test.sh $HOME/CK/ck-rigetti/t/pyquil_test.py | ck virtual env --tags=pyquil,needs-python-3.6.4
#   echo $HOME/CK/ck-rigetti/t/ck_pyquil_test.sh                                      | ck virtual env --tags=pyquil,needs-python-2.7.14

WHICH_PYTHON=${CK_ENV_COMPILER_PYTHON_FILE:-`which python`}
WHICH_TEST=${1:-$HOME/CK/ck-rigetti/t/pyquil_test.py}
PYTHON_VERSION=`$WHICH_PYTHON --version 2>&1`

echo "Running the test ${WHICH_TEST} using ${PYTHON_VERSION} @ ${WHICH_PYTHON}"
echo

$WHICH_PYTHON $WHICH_TEST

