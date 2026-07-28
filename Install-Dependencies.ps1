param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$Vendor = Join-Path $PSScriptRoot "vendor"

Write-Host "Installiere Abhängigkeiten ausschließlich nach:"
Write-Host "  $Vendor"

& $Python -m pip install `
    --upgrade `
    --target $Vendor `
    -r (Join-Path $PSScriptRoot "requirements.txt")

if ($LASTEXITCODE -ne 0) {
    throw "Download/Installation der Python-Abhängigkeiten fehlgeschlagen."
}

Write-Host "Abhängigkeiten wurden installiert."
Write-Host "Anschließend Build-Portable-EXE.ps1 ausführen."
