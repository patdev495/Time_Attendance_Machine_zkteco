$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}
try { [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe")) | Out-Null } catch {}

$asm = [System.Reflection.Assembly]::LoadFile("C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll")
$type = $asm.GetType("Hanvon.KMS.Business.BDeviceRelated")

if ($type -eq $null) {
    try {
        $types = $asm.GetTypes()
        $type = $types | Where-Object { $_ -ne $null -and $_.FullName -eq "Hanvon.KMS.Business.BDeviceRelated" }
    } catch [System.Reflection.ReflectionTypeLoadException] {
        $type = $_.Exception.Types | Where-Object { $_ -ne $null -and $_.FullName -eq "Hanvon.KMS.Business.BDeviceRelated" }
    }
}

if ($type) {
    if ($type -is [array]) {
        $type = $type[0]
    }
    Write-Host "Found Type: $($type.FullName)"
    $methods = $type.GetMethods([System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic)
    foreach ($m in $methods) {
        if ($m.Name -eq "DownRcdAndSave" -or $m.Name -eq "AutoSyncRcd") {
            Write-Host "Method: $($m.Name)"
            foreach ($p in $m.GetParameters()) {
                Write-Host "  Parameter: Name=$($p.Name), Type=$($p.ParameterType.FullName)"
            }
        }
    }
} else {
    Write-Host "BDeviceRelated type not found."
}
