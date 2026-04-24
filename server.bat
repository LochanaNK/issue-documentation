@echo on
title Fast API Server
:: Activate virtual environment
call venv\Scripts\activate

echo Starting Ollama service in the background...
start "" /min cmd /c "ollama run gemma4:e4b > nul 2>&1"

echo Starting Uvicorn Server...
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4

pause