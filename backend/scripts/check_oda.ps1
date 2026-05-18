$ErrorActionPreference = "Stop"

$default = "C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
$path = if ($env:ODAFC_EXEC_PATH) { $env:ODAFC_EXEC_PATH } else { $default }

if (-not $env:ODAFC_EXEC_PATH) {
    Write-Warning "ODAFC_EXEC_PATH not set; falling back to $default"
}

if (-not (Test-Path $path)) {
    Write-Error "ODA File Converter not found at: $path"
    Write-Error "Install from https://www.opendesign.com/guestfiles/oda_file_converter"
    exit 1
}

Write-Host "[ok] ODA File Converter found at: $path"
