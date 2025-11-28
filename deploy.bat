@echo off
echo ==========================================
echo   ContentTranscriber Deployment Script
echo ==========================================
echo.

echo [1/4] Building Frontend...
cd frontend
call npm install
call npm run build
if %errorlevel% neq 0 (
    echo Frontend build failed!
    pause
    exit /b
)
cd ..

echo.
echo [2/4] Copying files to Backend...
if exist "backend\static" rmdir /s /q "backend\static"
mkdir "backend\static"
xcopy /s /e /y "frontend\dist\*" "backend\static\"

echo.
echo [3/4] Google Cloud Configuration...
echo Please ensure you have run 'gcloud auth login' at least once.
echo.

set /p PROJECT_ID="Enter your Google Cloud Project ID: "
set /p GROQ_KEY="Enter your GROQ_API_KEY: "

echo.
echo [4/4] Deploying to Cloud Run...
cd backend
call gcloud config set project %PROJECT_ID%
call gcloud run deploy content-transcriber-api --source . --platform managed --region us-central1 --allow-unauthenticated --set-env-vars GROQ_API_KEY=%GROQ_KEY%

echo.
echo ==========================================
echo   Deployment Complete!
echo ==========================================
pause
