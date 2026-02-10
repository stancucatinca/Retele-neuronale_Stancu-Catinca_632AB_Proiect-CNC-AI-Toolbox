@echo off
echo ==========================================
echo    PORNIRE INTERFATA CNC-AI TOOLBOX
echo ==========================================
echo.
echo 1. Se verifica locatia Python...
echo Cale Python: C:\Users\Cati\AppData\Local\Python\pythoncore-3.14-64\python.exe
echo.
echo 2. Se porneste Streamlit...
echo Cale Fisier: C:\Users\Cati\Desktop\RN\src\app\interface.py
echo.

"C:\Users\Cati\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run "C:\Users\Cati\Desktop\RN\src\app\interface.py"

if %errorlevel% neq 0 (
    echo.
    echo [EROARE] Ceva nu a mers!
    echo Verifica daca fisierul 'interface.py' este exact in folderul:
    echo RN -> src -> app
    pause
)