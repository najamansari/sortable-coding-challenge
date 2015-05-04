#!/bin/bash

# Initializes the environment and runs the code.

# Check if the data files are present otherwise download them
echo "Looking for data files..."
if [ ! -f listings.txt ] || [ ! -f products.txt ]; then
    echo "Data files not found. Will attempt to download them..."
    wget https://s3.amazonaws.com/sortable-public/challenge/challenge_data_20110429.tar.gz
    tar -xvf challenge_data_20110429.tar.gz
    rm challenge_data_20110429.tar.gz
    echo "Data files downloaded successfully!"
fi

# Check if Pip is installed on the system
echo "Looking for the Pip Package Manager..."
if ! which pip 1> /dev/null; then
    echo "Pip could not be found on the system. Will attempt to download it now..."
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --user
    rm get-pip.py
    echo "Pip installed successfully!"
fi

# Check if virtualenv is installed on the system
echo "Looking for the Virtualenv utility..."
if ! which virtualenv 1> /dev/null; then
    echo "Virtualenv could not be found. Will attempt to install it..."
    pip install virtualenv
    echo "Virtualenv was installed successfully!"
fi

# Check if a virtual env exists otherwise create it
echo "Looking for a virtualenv named 'env'"
if [ ! -d env ]; then
    echo "Virtualenv not found. Creating one..."
    virtualenv -p /usr/bin/python2.7 env
    echo "Virtualenv created successfully!"
fi

# Activate the env
source env/bin/activate
echo "Virtualenv activated!"

# Install the dependencies
echo "Running a dependency check..."
pip install -r requirements.txt
echo "All dependencies installed!"

echo "Running the main program..."
if [ $# -eq 0 ]; then
    python challenge.py
else
    python challenge-es.py "$@"
fi

echo "All done!"