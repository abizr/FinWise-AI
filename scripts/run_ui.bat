@echo off
echo === Menjalankan FinWise UI (Streamlit) ===

call .venv\Scripts\activate

streamlit run app\ui.py

pause
