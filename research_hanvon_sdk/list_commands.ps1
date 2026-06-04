$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asm = [Reflection.Assembly]::LoadFile($HwDevOpPath)

$refType = $asm.GetType("Hanvon.FaceID.DevTypeReflection")
if ($refType) {
    # Instantiate or call static methods
    $getHWDevType = $refType.GetMethod("GetHWDevType")
    # Let's list sorted device type strings
    $getSortedList = $refType.GetMethod("GetSortedDevTypeStrList")
    $types = $getSortedList.Invoke($null, $null)
    
    foreach ($t in $types) {
        Write-Host "Device Type: $t"
        $devTypeObj = $getHWDevType.Invoke($null, @($t))
        if ($devTypeObj) {
            $cmdProp = $devTypeObj.GetType().GetProperty("CommandStrings")
            if ($cmdProp) {
                $cmds = $cmdProp.GetValue($devTypeObj, $null)
                Write-Host "  Commands:"
                foreach ($c in $cmds) {
                    Write-Host "    $c"
                }
            }
        }
        Write-Host "----------------------------------------"
    }
} else {
    Write-Host "DevTypeReflection not found."
}
