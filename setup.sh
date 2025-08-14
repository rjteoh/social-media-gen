#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Playwright browser..."
python -m playwright install

echo "Setup complete. You can now run:"
echo   "source venv/bin/activate   (to activate the venv)"
echo   "python main.py"