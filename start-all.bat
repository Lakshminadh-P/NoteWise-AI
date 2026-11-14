@echo off
echo ==========================================
echo    Starting NoteWise AI Full-Stack App
echo ==========================================
start "NoteWise Backend" cmd /k "%~dp0start-backend.bat"
timeout /t 2 /nobreak >nul
start "NoteWise Frontend" cmd /k "%~dp0start-frontend.bat"
echo Both servers are launching in separate windows!
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173
timeout /t 5 >nul
