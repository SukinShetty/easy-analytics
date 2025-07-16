@echo off
echo ==========================================
echo DEMO MODE - Test Chatbot Without Freshworks
echo ==========================================
echo.
echo Since your Freshworks API key has permission issues,
echo let's load demo data so you can test the chatbot!
echo.
pause

REM Install psycopg2 if needed
echo [*] Installing database driver...
pip install psycopg2-binary

echo.
echo [*] Loading demo CRM data...
python demo_mode_setup.py

echo.
echo ==========================================
echo WHAT TO DO NEXT:
echo ==========================================
echo.
echo 1. Open ToolJet: http://localhost:3000
echo 2. Follow CLIENT_DEMO_GUIDE.md to set up the chatbot
echo 3. Test with questions like:
echo    - "What is the total revenue this month?"
echo    - "Show me top 5 deals"
echo    - "Which product sells the most?"
echo.
echo Meanwhile, to fix Freshworks access:
echo    - Read GET_CORRECT_API_KEY.md
echo    - Get a proper CRM API key with permissions
echo.
start http://localhost:3000
pause 