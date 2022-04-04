#!/bin/bash -e

THIS_DIR = `dirname $0`
VENV_LOCATION = $THIS_DIR/.venv

help() {
  name = `basename "$0"`
  echo "Project Python Virtual Environment Setup Script"
  echo ""
  echo "Usage: $name"
  echo ""
  exit 1
}

install_python() {
  echo "Installing Python virtual environment to ./$VENV_LOCATION"
  [ -d "$VENV_LOCATION" ] && echo "remove previous Python's env: $VENV_LOCATION" && rm -rf $VENV_LOCATION
  PYTHON_LOCATION=$(which python3)
  virtualenv -p $PYTHON_LOCATION $VENV_LOCATION
}

install_packages(){
  echo "Installing dependency packages"
  source activate
  pip install pip\>=22.0.1
  poetry install --no-root
  deactivate
}

while getopts ":h" arg; do
  case $arg in
    h) help;;
  esac
done

cd $THIS_DIR
install_python
install_packages

exit 0