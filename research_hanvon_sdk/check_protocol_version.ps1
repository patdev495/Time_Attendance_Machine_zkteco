$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
$hwDevPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\hwDevice"

[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload assembly directories
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}
Get-ChildItem -Path $hwDevPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$FaceIdPath = Join-Path $clientPath "FaceId.dll"
$HwDevOpPath = Join-Path $clientPath "HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asm = [Reflection.Assembly]::LoadFile($HwDevOpPath)

$refType = $asm.GetType("Hanvon.FaceID.DevTypeReflection")

# Call InitDevTypeDict(path, search)
$initMethod = $refType.GetMethod("InitDevTypeDict")
$initMethod.Invoke($null, @($hwDevPath, "HW__*.dll"))

$getHWDevType = $refType.GetMethod("GetHWDevType")
$devTypeObj = $getHWDevType.Invoke($null, @("HW-D2"))

if ($devTypeObj) {
    $pvProp = $devTypeObj.GetType().GetProperty("ProtocolVersion")
    if ($pvProp) {
        $pv = $pvProp.GetValue($devTypeObj, $null)
        Write-Host "ProtocolVersion for HW-D2: $pv"
    } else {
        Write-Host "ProtocolVersion property not found."
    }
    
    $cmdProp = $devTypeObj.GetType().GetProperty("CommandStrings")
    if ($cmdProp) {
        $cmds = $cmdProp.GetValue($devTypeObj, $null)
        Write-Host "Supported Commands:"
        foreach ($c in $cmds) {
            Write-Host "  $c"
        }
    }
} else {
    Write-Host "HW-D2 device type not found."
}
