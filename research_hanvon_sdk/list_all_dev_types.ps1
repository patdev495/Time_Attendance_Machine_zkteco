$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asmOp = [Reflection.Assembly]::LoadFile($HwDevOpPath)
$interfaceType = $asmOp.GetType("Hanvon.FaceID.IHWDevType")

if (-not $interfaceType) {
    Write-Host "IHWDevType not found."
    exit
}

$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try {
        $asm = [Reflection.Assembly]::LoadFile($_.FullName)
        foreach ($t in $asm.GetTypes()) {
            if ($t.IsClass -and $interfaceType.IsAssignableFrom($t)) {
                try {
                    $instance = [System.Activator]::CreateInstance($t)
                    $pv = $t.GetProperty("ProtocolVersion").GetValue($instance, $null)
                    $name = $t.GetProperty("LocalizedDisplayStr").GetValue($instance, $null)
                    Write-Host "DLL: $($_.Name), Class: $($t.FullName), Name: $name, ProtocolVersion: $pv"
                } catch {
                    Write-Host "DLL: $($_.Name), Class (no ctor): $($t.FullName) - Error: $($_.Exception.Message)"
                }
            }
        }
    } catch {
        Write-Host "Error loading $($_.Name): $($_.Exception.Message)"
    }
}
