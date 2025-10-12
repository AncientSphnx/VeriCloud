@echo off
echo Starting All Lie Detector Backends...
echo.

echo Starting Authentication Backend on port 5001...
start "Auth Backend" cmd /k "python server.py"
timeout /t 2 /nobreak >nul

echo Starting Text Backend on port 8000...
start "Text Backend" cmd /k "cd Text && uvicorn app:app --reload --port 8000"
timeout /t 2 /nobreak >nul

echo Starting Voice Backend on port 8001...
start "Voice Backend" cmd /k "cd Voice && uvicorn app:app --reload --port 8001"
timeout /t 2 /nobreak >nul

echo Starting Fusion Backend on port 8002...
start "Fusion Backend" cmd /k "cd Fusion && uvicorn app:app --reload --port 8002"

echo.
echo All backends started!
echo Auth Backend:   http://127.0.0.1:5001
echo Text Backend:   http://127.0.0.1:8000
echo Voice Backend:  http://127.0.0.1:8001
echo Fusion Backend: http://127.0.0.1:8002
echo.
pause
