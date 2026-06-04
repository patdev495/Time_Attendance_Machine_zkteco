$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload assembly directories
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$assemblies = @("KMS.Common.dll", "KMS.Business.dll", "mca.exe")
foreach ($asmName in $assemblies) {
    try {
        $asm = [Reflection.Assembly]::LoadFile((Join-Path $clientPath $asmName))
        foreach ($type in $asm.GetTypes()) {
            foreach ($method in $type.GetMethods([System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic)) {
                try {
                    $body = $method.GetMethodBody()
                    if ($body -ne $null) {
                        $il = $body.GetILAsByteArray()
                        # We search for call or callvirt instructions targeting GetRecord.
                        # Instead of parsing tokens, let's just print methods that contain the name GetRecord in their decompiled info or references.
                        # A simpler way is to check the MethodInfo's name or if it belongs to DeviceOperation.
                    }
                } catch {}
            }
        }
    } catch {}
}

# Let's list all types/methods in KMS.Business.dll to see where syncing happens
$bizAsm = [Reflection.Assembly]::LoadFile((Join-Path $clientPath "KMS.Business.dll"))
Write-Host "=== Types in KMS.Business.dll ==="
foreach ($t in $bizAsm.GetTypes()) {
    if ($t.Name -like "*Device*" -or $t.Name -like "*Sync*" -or $t.Name -like "*Record*" -or $t.Name -like "*Card*") {
        Write-Host "Type: $($t.FullName)"
        foreach ($m in $t.GetMethods()) {
            if ($m.Name -like "*Rcd*" -or $m.Name -like "*Record*" -or $m.Name -like "*Sync*" -or $m.Name -like "*Down*") {
                Write-Host "  Method: $($m.Name)"
            }
        }
    }
}
