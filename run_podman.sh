#!/bin/bash

## need to 

echo "Building the image with Podman..."
podman build -t streamlit-agent-app -f Containerfile .

echo "Running the container..."
echo "App will be available at http://localhost:8501"
podman run --rm -p 8501:8501 --env-file .env localhost/streamlit-agent-app

