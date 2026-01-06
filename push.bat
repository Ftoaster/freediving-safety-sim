@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "UI update: time display style, safety turn time"
git push origin main
pause
