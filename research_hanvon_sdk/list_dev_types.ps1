$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asm = [Reflection.Assembly]::LoadFile($HwDevOpPath)

$interfaceType = $asm.GetType("Hanvon.FaceID.IHWDevType")
if ($interfaceType) {
    foreach ($t in $asm.GetTypes()) {
        if ($t.IsClass -and $interfaceType.IsAssignableFrom($t)) {
            try {
                $instance = [System.Activator]::CreateInstance($t)
                $pv = $t.GetProperty("ProtocolVersion").GetValue($instance, $null)
                $name = $t.GetProperty("LocalizedDisplayStr").GetValue($instance, $null)
                Write-Host "Class: $($t.FullName), Name: $name, ProtocolVersion: $pv"
            } catch {
                # Some might not have parameterless constructor
                Write-Host "Class (no ctor): $($t.FullName)"
            }
        }
    }
} else {
    Write-Host "IHWDevType interface not found."
}
