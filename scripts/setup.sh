#!/bin/bash
# Setup script for initial project configuration

echo "Setting up F1 Service System..."

# Install dependencies with Poetry
echo "Installing dependencies..."
poetry install

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env with your API keys before running the application."
fi

# Create logs directory
mkdir -p logs

echo "Setup complete!"
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Run 'poetry shell' to activate the virtual environment"
echo "3. Run 'bash scripts/run_app.sh' to start the application"
