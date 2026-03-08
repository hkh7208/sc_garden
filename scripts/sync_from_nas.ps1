[CmdletBinding()]
param(
    [string]$ProjectRoot = "G:\VS_code\sc_garden",
    [string]$NasIp = "192.168.0.250",
    [string]$NasMediaShare = "web\sc_garden\media",
    [switch]$SkipMedia
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & $Action
}

if (-not (Test-Path $ProjectRoot)) {
    throw "Project root not found: $ProjectRoot"
}

Set-Location $ProjectRoot

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python executable not found: $python"
}

$backupDir = Join-Path $ProjectRoot "backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$localBackup = Join-Path $backupDir "local_before_sync_$timestamp.json"
$nasDump = Join-Path $backupDir "nas_appdata_$timestamp.json"

$env:PYTHONUTF8 = "1"

Invoke-Step "DB connectivity check" {
    & $python manage.py shell -c "from django.db import connections; aliases=['nas','local'];
for a in aliases:
    c=connections[a].cursor(); c.execute('SELECT 1'); print(a, 'OK')"
    if ($LASTEXITCODE -ne 0) { throw "DB connectivity check failed." }
}

Invoke-Step "Backup local DB" {
    & $python manage.py dumpdata --database local --indent 2 --output $localBackup
    if ($LASTEXITCODE -ne 0) { throw "Failed to backup local DB." }
}

Invoke-Step "Dump NAS app data" {
    & $python manage.py dumpdata --database nas --exclude contenttypes --exclude auth.permission --exclude admin.logentry --indent 2 --output $nasDump
    if ($LASTEXITCODE -ne 0) { throw "Failed to dump NAS app data." }
}

Invoke-Step "Restore local DB from NAS dump" {
    & $python manage.py flush --database local --noinput
    if ($LASTEXITCODE -ne 0) { throw "Failed to flush local DB." }

    & $python manage.py loaddata --database local $nasDump
    if ($LASTEXITCODE -ne 0) { throw "Failed to restore local DB." }
}

if (-not $SkipMedia) {
    Invoke-Step "Mirror media from NAS" {
        $source = "\\$NasIp\$NasMediaShare"
        $dest = Join-Path $ProjectRoot "media"

        if (-not (Test-Path $source)) {
            throw "NAS media source not found: $source"
        }

        robocopy $source $dest /MIR /R:2 /W:2 /MT:16 /NFL /NDL /NP | Out-Null
        $rc = $LASTEXITCODE
        if ($rc -gt 7) {
            throw "Robocopy failed with exit code $rc"
        }

        Write-Host "Robocopy exit code: $rc" -ForegroundColor DarkGray
    }
}

Invoke-Step "Post-sync validation" {
    & $python manage.py shell -c "from portfolio.models import Season, Zone, Tag, Photo
for m in [Season, Zone, Tag, Photo]:
    nas=m.objects.using('nas').count(); local=m.objects.using('local').count(); print(f'{m.__name__}: nas={nas}, local={local}')"
    if ($LASTEXITCODE -ne 0) { throw "Validation query failed." }
}

Write-Host "`nSync complete." -ForegroundColor Green
Write-Host "Local backup: $localBackup"
Write-Host "NAS dump:     $nasDump"
