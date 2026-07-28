$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$Stamp = Get-Date -Format "yyyyMMdd_HHmm"
$Destination = Join-Path (Split-Path $ProjectRoot -Parent) (
    "NLCurrent2GRIB_v0.2.1_GitHub_Upload_$Stamp"
)

New-Item -ItemType Directory -Path $Destination -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Destination "app") -Force |
    Out-Null

foreach ($name in @(
    ".gitignore",
    "Build-Portable-EXE.ps1",
    "convert_cli.py",
    "Install-Dependencies.ps1",
    "LICENSE",
    "Prepare-GitHub-Upload.ps1",
    "README.md",
    "requirements.txt",
    "run_gui.py",
    "THIRD_PARTY_NOTICES.txt"
)) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $name) `
        -Destination $Destination -Force
}

Copy-Item -Path (Join-Path $ProjectRoot "app\*.py") `
    -Destination (Join-Path $Destination "app") -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "licenses") `
    -Destination $Destination -Recurse -Force

$Forbidden = Get-ChildItem -LiteralPath $Destination -Recurse -File |
    Where-Object {
        $_.Extension -in ".exe", ".dll", ".pyd", ".pyc", ".zip", ".grb", ".grb2"
    }
if ($Forbidden) {
    throw "Uploadordner enthält unerwartete Binär- oder Ausgabedateien."
}

Write-Host ""
Write-Host "GitHub-Uploadordner wurde erzeugt:"
Write-Host $Destination
