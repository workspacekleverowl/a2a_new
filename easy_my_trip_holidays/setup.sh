#!/bin/bash

# This script installs dependencies for all agents

# List of all agent directories
AGENT_DIRS=(
    "travel_planner_host"
    "flight_agent"
    "hotel_agent"
    "cab_agent"
    "activity_agent"
    "weather_agent"
    "budget_agent"
    "document_agent"
    "food_agent"
    "currency_agent"
)

# Loop through each directory and install dependencies
for DIR in "${AGENT_DIRS[@]}"; do
    echo "--- Setting up environment for $DIR ---"
    cd "$DIR"
    uv venv
    uv pip install -r requirements.txt
    cd ..
    echo "--- Done with $DIR ---"
    echo ""
done

echo "All dependencies installed successfully!"