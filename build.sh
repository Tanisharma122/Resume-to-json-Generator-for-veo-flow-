#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating required directories..."
mkdir -p uploads
mkdir -p outputs

echo "Build completed successfully!"
