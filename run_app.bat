@echo off
where uv >nul 2>nul
if errorlevel 1 (
    echo uv is not installed. Install it from https://docs.astral.sh/uv/ and re-run.
    exit /b 1
)

uv sync
if errorlevel 1 exit /b %errorlevel%

uv run python -m app.app
