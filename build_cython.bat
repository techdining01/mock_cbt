@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo             BUILDING SECURE LLS CBT (CYTHON + PYINSTALLER)
echo ==============================================================================
echo.

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)

echo [1/4] Installing build requirements...
%PYTHON_EXE% -m pip install --quiet cython pyinstaller setuptools

echo [2/4] Compiling core application to native C (.pyd)...
%PYTHON_EXE% -c "from setuptools import setup; from Cython.Build import cythonize; import glob; setup(ext_modules=cythonize(glob.glob('app/**/*.py', recursive=True), compiler_directives={'language_level': '3'}))" build_ext --inplace

echo [3/4] Packaging standalone bundle with PyInstaller...
%PYTHON_EXE% -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "LLS-CBT" ^
    --icon "app/web/images/company_logo.ico" ^
    --add-data "app/web;app/web" ^
    --add-data "data;data" ^
    --collect-all "pyside6" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "cryptography" ^
    --hidden-import "pydantic" ^
    --collect-all "uvicorn" ^
    --collect-all "fastapi" ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/4] Build finished successfully!
echo Distribution bundle created at: dist\LLS-CBT\
echo.
pause

