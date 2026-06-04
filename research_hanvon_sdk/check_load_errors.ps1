$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

Write-Host "=== Loading DLLs ==="
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try {
        [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null
        Write-Host "Loaded: $($_.Name)"
    } catch {
        Write-Host "Failed: $($_.Name) - $_"
    }
}

Write-Host "`n=== Loading EXE ==="
try {
    [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe")) | Out-Null
    Write-Host "Loaded: mca.exe"
} catch {
    Write-Host "Failed: mca.exe - $_"
}
