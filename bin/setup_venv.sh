#!/usr/bin/env bash
# Run this from the project directory
# Downloads python 2.7.9
# Install it in the project directory (where we have write access)
# Load a venv with this python
# Loads other dependencies into the venv.

# Get present working directory
pwd=$(pwd)

# Get Python sources and compile
wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar xfz Python-2.7.9.tgz
cd Python-2.7.9/ || exit
make clean
./configure --prefix="$pwd"/.localpython
make
make install
cd ..

# Load it into a virutal environment titled venv_invite
virtualenv -p "$pwd"/.localpython/bin/python venv_invite

# load and prepare the venv
. venv_invite/bin/activate
pip install -r requirements.txt
deactivate
