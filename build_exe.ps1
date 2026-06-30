$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install "pyinstaller>=6.0,<8.0"

.\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --noupx `
    --name "GeneradorIconos" `
    .\icono.py

Write-Host ""
Write-Host "EXE generado en: .\dist\GeneradorIconos\GeneradorIconos.exe"
