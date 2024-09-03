#!/bin/bash -e

THIS_DIR=`dirname $0`
VENV_LOCATION=$THIS_DIR/.venv

if [ x"${VENV_LOCATION}" = xnull ] || [ x"${VENV_LOCATION}" = x"" ]; then
  VENV_LOCATION=$THIS_DIR/.venv
fi

PYTHON_EXECUTABLE="python"


install_python(){
  echo "Installing Python virtual environment to ./$VENV_LOCATION"
  [ -d "$VENV_LOCATION" ] && echo "Remove previous Python's env: $VENV_LOCATION" && rm -rf $VENV_LOCATION
  PYTHON_LOCATION=$(which ${PYTHON_EXECUTABLE})
  $PYTHON_LOCATION -m venv $VENV_LOCATION
}

check_poetry() {
  echo "Verifying Poetry Installation."
  if command -v poetry &> /dev/null ; then
    echo "Poetry installed."
  else
    echo "ERROR: Poetry not installed. Please install it."
    exit 1
  fi
}

install_packages(){
  echo "Installing dependency packages"
  source activate
  pip install pip\>=22.3.1
  poetry install --with=dev --no-root
  echo $(pip list)
  deactivate
}

while getopts ":h" arg; do
  case $arg in
    h) help;;
  esac
done

cd $THIS_DIR
install_python && check_poetry && install_packages

exit 0