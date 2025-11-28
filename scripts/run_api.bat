@echo off
echo === Menjalankan FinWise API (FastAPI) ===

call .venv\Scripts\activate

set UV_HOST=127.0.0.1
set UV_PORT=8000

echo Host: %UV_HOST%  Port: %UV_PORT%
uvicorn app.main:app --reload --host %UV_HOST% --port %UV_PORT%

pause
