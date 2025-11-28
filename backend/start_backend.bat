@echo off
echo Installing dependencies...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo "py command failed, trying python..."
    python -m pip install -r requirements.txt
)

echo Starting server...
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
)
pause
