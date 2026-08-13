#!/bin/bash
# Create python virtual environment and install requirements
echo "Creating virtual environment in venv/..."
python3 -m venv venv
source venv/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "Environment setup complete!"
