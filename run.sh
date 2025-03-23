#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Flask application
echo "Starting the server..."
python app.py
