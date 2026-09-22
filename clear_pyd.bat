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


@echo off
echo Close the LLS-CBT app completely before running this.
echo.
pause

echo Deleting stale .pyd files...
for /r "app" %%f in (*.pyd) do (
    del /f /q "%%f" 2>nul && echo   Deleted: %%f
)
echo.
echo Done. You can now run the app with: uv run python main.py
pause
