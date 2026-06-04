$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"

# 1. Load KMS.Common.dll in isolation and print matching types
$asmCommon = [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "KMS.Common.dll"))
Write-Host "KMS.Common.dll loaded. Types count:"
try {
    $types = $asmCommon.GetTypes()
    Write-Host "  Success: $($types.Count)"
    $types | Where-Object { $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName)" }
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "  RTLE: $($_.Exception.LoaderExceptions.Message)"
    $_.Exception.Types | Where-Object { $_ -ne $null -and $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName) (RTLE)" }
}

# 2. Load KMS.Business.dll in isolation and print matching types
$asmBusiness = [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "KMS.Business.dll"))
Write-Host "`nKMS.Business.dll loaded. Types count:"
try {
    $types = $asmBusiness.GetTypes()
    Write-Host "  Success: $($types.Count)"
    $types | Where-Object { $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName)" }
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "  RTLE: $($_.Exception.LoaderExceptions.Message)"
    $_.Exception.Types | Where-Object { $_ -ne $null -and $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName) (RTLE)" }
}

# 3. Load mca.exe in isolation and print matching types
$asmMca = [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe"))
Write-Host "`nmca.exe loaded. Types count:"
try {
    $types = $asmMca.GetTypes()
    Write-Host "  Success: $($types.Count)"
    $types | Where-Object { $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName)" }
} catch [System.Reflection.ReflectionTypeLoadException] {
    Write-Host "  RTLE: $($_.Exception.LoaderExceptions.Message)"
    $_.Exception.Types | Where-Object { $_ -ne $null -and $_.FullName -like "*BDeviceRelated*" } | ForEach-Object { Write-Host "    - $($_.FullName) (RTLE)" }
}
