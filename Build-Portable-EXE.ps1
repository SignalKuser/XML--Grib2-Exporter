param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$Vendor = Join-Path $ProjectRoot "vendor"
$env:PYTHONPATH = $Vendor

if (-not (Test-Path -LiteralPath (Join-Path $Vendor "PyInstaller"))) {
    throw "Build-Abhängigkeiten fehlen. Zuerst Install-Dependencies.ps1 ausführen."
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name NLCurrent2GRIB_v021 `
    --paths $Vendor `
    --collect-all eccodes `
    --collect-all eccodeslib `
    --collect-all tkinterdnd2 `
    (Join-Path $ProjectRoot "run_gui.py")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller-Build fehlgeschlagen."
}

$Portable = Join-Path $ProjectRoot "dist\NLCurrent2GRIB_v021"
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") `
    -Destination $Portable -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "THIRD_PARTY_NOTICES.txt") `
    -Destination $Portable -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "LICENSE") `
    -Destination $Portable -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "licenses") `
    -Destination $Portable -Recurse -Force

Write-Host ""
Write-Host "NLCurrent2GRIB V0.2.1 wurde erfolgreich gebaut."
Write-Host "Portable Ausgabe:"
Write-Host $Portable
