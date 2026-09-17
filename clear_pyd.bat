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
