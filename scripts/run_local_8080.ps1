[CmdletBinding()]
param(
    [string]$ProjectRoot = "G:\VS_code\sc_garden",
    [string]$AddrPort = "127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ProjectRoot)) {
    throw "Project root not found: $ProjectRoot"
}

Set-Location $ProjectRoot

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python executable not found: $python"
}

$env:SERVER_PROFILE = "local"
$env:DB_HOST_MODE = "local"

Write-Host "Starting local server at http://$AddrPort/" -ForegroundColor Cyan
& $python manage.py runserver $AddrPort
