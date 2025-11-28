@echo off
echo === FinWise AI - Environment Setup (Windows) ===

where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo Python tidak ditemukan. Install dulu Python 3.10+.
    pause
    exit /b 1
)

IF NOT EXIST .venv (
    echo Membuat virtual environment .venv ...
    python -m venv .venv
) ELSE (
    echo Virtual env .venv sudah ada, skip.
)

call .venv\Scripts\activate

echo Update pip...
python -m pip install --upgrade pip

echo Install dependencies dari requirements.txt ...
pip install -r requirements.txt

echo.
echo === Selesai setup ===
echo Untuk mengaktifkan env:
echo   .venv\Scripts\activate
echo Jalankan API dengan:
echo   scripts\run_api.bat
echo Jalankan UI dengan:
echo   scripts\run_ui.bat
pause
