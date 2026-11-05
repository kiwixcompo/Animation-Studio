@echo off
cd /d "%~dp0"
echo Starting Animation Studio Web App (Streamlit)...
"C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py --server.port 8501 --server.headless true
pause
