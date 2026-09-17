@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo                 LLS-CBT BUILD - CYTHON + PYINSTALLER
echo ==============================================================================

echo.


rem ============================================================
rem PRE-CLEAN: delete stale .pyd and .c files BEFORE ANY step
rem Run this BEFORE starting the numbered steps 9-step build proper to avoid
rem cmd / parser traps with stale compiled extensions taking precedence
rem over new .py sources.
rem ============================================================

echo [PRE-CLEAN] Deleting stale .pyd / .c / __pycache__ ...
echo.

for /r "app" %%f in (*.pyd) do (
    del /f /q "%%f" 2>nul && echo   Deleted ^(app^): %%f
)
for %%f in (*.pyd) do (
    del /f /q "%%f" 2>nul && echo   Deleted ^(root^): %%f
)
for /r "app" %%f in (*.c) do (
    del /f /q "%%f" 2>nul
)
for %%f in (*.c) do (
    del /f /q "%%f" 2>nul
)
for /d /r "app" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo [PRE-CLEAN] Done. Old .pyd files removed. Now you can be sure .py sources
echo            will be Cythonised this build.
echo.


rem ============================================================
rem PYTHON
rem ============================================================

set "PYTHON_EXE=python"

if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [INFO] Python:
%PYTHON_EXE% --version

echo [INFO] Python executable:
%PYTHON_EXE% -c "import sys; print(sys.executable)"

echo.


rem ============================================================
rem CHECK REQUIRED FILES
rem ============================================================

echo [1/9] Checking project files...

if exist "main.py" goto :have_main
echo [ERROR] main.py not found.
pause
exit /b 1
:have_main

if exist "LLS-CBT.spec" goto :have_spec
echo [ERROR] LLS-CBT.spec not found.
pause
exit /b 1
:have_spec

if exist "app\web\index.html" goto :have_html
echo [ERROR] app\web\index.html not found.
pause
exit /b 1
:have_html

if exist "app\ai_tutor\router.py" goto :have_router
echo [ERROR] app\ai_tutor\router.py not found.
pause
exit /b 1
:have_router

if exist "app\ai_tutor\schemas.py" goto :have_schemas
echo [ERROR] app\ai_tutor\schemas.py not found.
pause
exit /b 1
:have_schemas

if exist "app\ai_tutor\services\providers\gemini.py" goto :have_gemini
echo [ERROR] Gemini provider not found.
pause
exit /b 1
:have_gemini

if exist "question_import_launcher.py" goto :have_qi
echo [ERROR] question_import_launcher.py not found.
pause
exit /b 1
:have_qi

echo [OK] Required files found.

echo.


rem ============================================================
rem INSTALL BUILD DEPENDENCIES
rem ============================================================

echo [2/9] Installing build dependencies...

%PYTHON_EXE% -m pip install --upgrade cython pyinstaller setuptools fastapi uvicorn google-genai httpx python-dotenv >nul 2>&1

echo [OK] Build dependencies ready.

echo.


rem ============================================================
rem VERIFY SSL BEFORE BUILD
rem ============================================================

echo [3/9] Verifying Python SSL runtime...

%PYTHON_EXE% -c "import ssl; import _ssl; import hashlib; import _hashlib; import sys; print('Python:', sys.executable); print('OpenSSL:', ssl.OPENSSL_VERSION); print('_ssl:', _ssl.__file__); print('_hashlib:', _hashlib.__file__); print('SSL OK')"

if not errorlevel 1 goto :ssl_ok
echo.
echo [ERROR] Python SSL is NOT working in the build environment.
echo.
echo The application cannot be packaged correctly until this works.
echo.
pause
exit /b 1
:ssl_ok

echo [OK] Python SSL runtime is working.

echo.


rem ============================================================
rem CLEAN BUILD / DIST ARTIFACTS (build\ and dist\ (step [4/9]
rem ============================================================

echo [4/9] Cleaning previous build artifacts...

if not exist "build" goto :skip_build_rm
rmdir /s /q "build"
:skip_build_rm

if not exist "dist\LLS-CBT" goto :skip_dist_rm
rmdir /s /q "dist\LLS-CBT"
:skip_dist_rm

if not exist "dist\LLS-CBT.exe" goto :skip_exe_rm
del /q "dist\LLS-CBT.exe"
:skip_exe_rm

echo [OK] Build / dist artifacts cleaned.

echo.


rem ============================================================
rem CYTHON
rem ============================================================

echo [5/9] Compiling Cython modules (16 total)...

%PYTHON_EXE% setup.py build_ext --inplace

if not errorlevel 1 goto :cython_ok
echo.
echo [ERROR] Cython compilation failed.
pause
exit /b 1
:cython_ok

echo [OK] Cython compilation completed.

echo.


rem ============================================================
rem VERIFY AI
rem ============================================================

echo [6/9] Verifying AI imports...

set AI_VERIFY_FAILED=0

%PYTHON_EXE% -c "import app.ai_tutor.router; print('  app.ai_tutor.router              OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.schemas; print('  app.ai_tutor.schemas             OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.ai_settings_resolver; print('  app.ai_tutor.ai_settings_resolver OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.response_validator; print('  app.ai_tutor.response_validator  OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.providers.base; print('  app.ai_tutor.providers.base      OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.providers.provider_manager; print('  app.ai_tutor.providers.mgr       OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.providers.ollama; print('  app.ai_tutor.providers.ollama    OK - PRIMARY')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.providers.gemini; print('  app.ai_tutor.providers.gemini    OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.services.providers.remote_server; print('  app.ai_tutor.providers.remote    OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.ai_tutor.main; print('  app.ai_tutor.main                OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import app.services.settings_service; print('  app.services.settings_service    OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

%PYTHON_EXE% -c "import fastapi, uvicorn, google.genai, httpx; print('  fastapi/uvicorn/httpx/google-genai OK')"
if errorlevel 1 set AI_VERIFY_FAILED=1

if not "%AI_VERIFY_FAILED%"=="1" goto :ai_verify_ok
echo.
echo [ERROR] One or more AI modules failed to import. See messages above.
pause
exit /b 1
:ai_verify_ok

echo [OK] All AI modules verified.

echo.


rem ============================================================
rem PYINSTALLER
rem ============================================================

echo [7/9] Building LLS-CBT with PyInstaller...

%PYTHON_EXE% -m PyInstaller LLS-CBT.spec --noconfirm --clean

if not errorlevel 1 goto :pyi_ok
echo.
echo [ERROR] PyInstaller failed.
pause
exit /b 1
:pyi_ok

echo [OK] PyInstaller completed.

echo.


rem ============================================================
rem VERIFY PACKAGE
rem ============================================================

echo [8/9] Verifying packaged application...

if exist "dist\LLS-CBT\LLS-CBT.exe" goto :have_exe
echo [ERROR] LLS-CBT.exe was not created.
pause
exit /b 1
:have_exe

echo [OK] LLS-CBT.exe exists.


if exist "dist\LLS-CBT\_internal\app\web\index.html" goto :have_web
echo [ERROR] Web assets missing from package.
pause
exit /b 1
:have_web

echo [OK] Web assets exist.


rem ============================================================
rem VERIFY SSL FILES IN DIST
rem ============================================================

echo.
echo [SSL] Checking packaged SSL files...

if not exist "dist\LLS-CBT\_ssl.pyd" goto :ssl_pyd_missing
echo [OK] _ssl.pyd found.
goto :ssl_pyd_done
:ssl_pyd_missing
echo [ERROR] _ssl.pyd NOT FOUND in packaged application.
:ssl_pyd_done

if not exist "dist\LLS-CBT\_hashlib.pyd" goto :hash_pyd_missing
echo [OK] _hashlib.pyd found.
goto :hash_pyd_done
:hash_pyd_missing
echo [ERROR] _hashlib.pyd NOT FOUND in packaged application.
:hash_pyd_done

dir /b "dist\LLS-CBT\libssl*.dll" 2>nul

dir /b "dist\LLS-CBT\libcrypto*.dll" 2>nul


rem ============================================================
rem COPY DATABASE
rem ============================================================

if not exist "data\cbt.sqlite3" goto :skip_db_copy

if exist "dist\LLS-CBT\data" goto :have_dbdir
mkdir "dist\LLS-CBT\data"
:have_dbdir

copy /y "data\cbt.sqlite3" "dist\LLS-CBT\data\cbt.sqlite3" >nul

echo [OK] Database copied.

:skip_db_copy


rem ============================================================
rem COMPLETE
rem ============================================================

echo.
echo [9/9] BUILD COMPLETE
echo.

echo ==============================================================================
echo                         BUILD COMPLETE
echo ==============================================================================
echo.
echo Output:
echo.
echo     dist\LLS-CBT\
echo.
echo Executable:
echo.
echo     dist\LLS-CBT\LLS-CBT.exe
echo.
echo IMPORTANT:
echo.
echo This is the production GUI build.
echo Console window is disabled.
echo.
echo ==============================================================================

pause

endlocal
