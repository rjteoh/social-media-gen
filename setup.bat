@echo off
echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Installing Playwright browsers...
python -m playwright install

echo Setup complete. You can now run:
echo   .venv\Scripts\activate   (to activate the venv)
echo   python main.py
pause