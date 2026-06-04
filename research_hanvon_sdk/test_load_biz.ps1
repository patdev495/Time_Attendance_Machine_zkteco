$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$asm = [System.Reflection.Assembly]::LoadFile("C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Business.dll")
try {
    $t = $asm.GetType("Hanvon.KMS.Business.BDeviceRelated")
    if ($t -eq $null) {
        Write-Host "GetType returned null."
    } else {
        Write-Host "Found type: $($t.FullName)"
    }
} catch {
    Write-Host "GetType threw error: $_"
}

try {
    $types = $asm.GetTypes()
    Write-Host "GetTypes returned $($types.Count) types."
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "ReflectionTypeLoadException caught."
    foreach ($le in $_.Exception.LoaderExceptions) {
        Write-Host "  LoaderException: $($le.Message)"
    }
    $loadedTypes = $_.Exception.Types | Where-Object { $_ -ne $null }
    Write-Host "Successfully loaded $($loadedTypes.Count) types:"
    foreach ($lt in $loadedTypes) {
        if ($lt.Name -like "*Device*" -or $lt.Name -like "*Sync*") {
            Write-Host "    $($lt.FullName)"
        }
    }
} catch {
    Write-Host "Other GetTypes error: $_"
}
