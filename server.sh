#!/bin/bash

# 1. Pre-load the model on the Windows host from inside the container
echo "🧠 Pre-loading Gemma model on host..."
curl -X POST http://host.docker.internal:11434/api/generate -d "{\"model\": \"gemma4:e4b\"}" > /dev/null

echo "🚀 Starting Uvicorn Server..."
# 2. Start the FastAPI server
# We use 'exec' so the container can shut down gracefully
exec uvicorn server:app --host 0.0.0.0 --port 8000 --reload \
    --reload-exclude 'input_docs/*' \
    --reload-exclude 'processed_docs/*' \
    --reload-exclude 'docs_db/*'