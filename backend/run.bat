@echo off
if not exist venv (
    echo Virtual environment not found. Please run: python -m venv venv
    exit /b
)
call venv\Scripts\activate
python init_db.py
python app.py
