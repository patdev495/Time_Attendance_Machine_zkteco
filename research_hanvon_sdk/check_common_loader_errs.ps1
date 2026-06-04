$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$asm = [System.Reflection.Assembly]::LoadFile("C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll")
try {
    $types = $asm.GetTypes()
    Write-Host "GetTypes succeeded. Count: $($types.Count)"
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "ReflectionTypeLoadException caught."
    foreach ($le in $_.Exception.LoaderExceptions) {
        Write-Host "  LoaderException: $($le.Message)"
    }
}
