@echo off
cd /d "%~dp0"
echo ========================================================
echo  Syncing Animation Studio to GitHub and Netlify...
echo ========================================================

git add .
set /p commit_msg="Enter commit message (or press enter for default): "
if "%commit_msg%"=="" set commit_msg="update: Animation Studio enhancement"

git commit -m "%commit_msg%"
git push origin main

echo ========================================================
echo  Changes pushed to GitHub successfully!
echo  Netlify is automatically building and deploying.
echo ========================================================
pause
