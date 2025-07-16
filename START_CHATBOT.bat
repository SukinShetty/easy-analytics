@echo off
echo ================================================================
echo        🎯 KAMBAA CRM ANALYTICS CHATBOT
echo                   Starting Server...
echo ================================================================
echo.

echo [*] Checking if server is already running...
netstat -ano | findstr :5000 >nul
if %errorlevel% == 0 (
    echo ✅ Server is already running on port 5000
    echo 🌐 Open: http://localhost:5000
    goto :end
)

echo [*] Starting Kambaa CRM Chatbot...
echo.
echo 📊 Loading real CRM data:
echo    • Sales Team: 4 members
echo    • Appointments: 25 meetings  
echo    • Contact Statuses: 9 pipeline stages
echo.

python simple_crm_chatbot.py

:end
echo.
echo ================================================================
echo 🌐 Your chatbot is ready at: http://localhost:5000
echo ================================================================
echo.
echo 💬 Try asking:
echo    "Who are our active sales team members?"
echo    "Show me meetings with Nestle"
echo    "What appointments do we have?"
echo.
pause 