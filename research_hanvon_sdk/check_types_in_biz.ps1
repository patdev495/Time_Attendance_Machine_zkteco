$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload DLLs
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$asm = [System.Reflection.Assembly]::LoadFile("C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Business.dll")
Write-Host "Assembly loaded: $($asm.FullName)"

try {
    $types = $asm.GetTypes()
    Write-Host "GetTypes() succeeded. Total types: $($types.Count)"
    foreach ($t in $types) {
        Write-Host "  Type: $($t.FullName)"
    }
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "GetTypes() threw ReflectionTypeLoadException!"
    Write-Host "Loader Exceptions:"
    foreach ($le in $_.Exception.LoaderExceptions) {
        Write-Host "  - $($le.Message)"
    }
    Write-Host "Types in Exception.Types:"
    $i = 0
    foreach ($t in $_.Exception.Types) {
        if ($t -eq $null) {
            Write-Host "  [$i] null"
        } else {
            Write-Host "  [$i] $($t.FullName)"
        }
        $i++
    }
} catch {
    Write-Host "Other Exception: $_"
}
