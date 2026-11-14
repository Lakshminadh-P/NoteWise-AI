@echo off
echo ==========================================
echo    Starting NoteWise AI Frontend Server
echo ==========================================
cd /d "%~dp0frontend"
npm run dev
pause
