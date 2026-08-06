@echo off
rem Launch the Fantasy Football Lab (Windows).
rem Double-click this file. A terminal window opens, then your browser.
rem Keep the terminal window open while using the lab; close it when done.
cd /d "%~dp0"
uv run jupyter lab --notebook-dir=notebooks
pause
