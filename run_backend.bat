@echo off
title NEXCIV FastAPI Backend
echo ========================================================
echo Starting NEXCIV FastAPI Backend on http://localhost:8000
echo ========================================================
call .venv\Scripts\activate.bat
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
