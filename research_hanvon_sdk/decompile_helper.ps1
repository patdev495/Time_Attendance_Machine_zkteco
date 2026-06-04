$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($HwDevOpPath) | Out-Null

$type = [Hanvon.FaceID.MessageTransfered]

$methods = @("SetMessage", "GetMessage")
foreach ($mName in $methods) {
    $method = $type.GetMethod($mName, [type[]]@([string]))
    if ($method) {
        Write-Host "--- Method: $mName ---"
        $body = $method.GetMethodBody()
        if ($body) {
            $ilBytes = $body.GetILAsByteArray()
            $ilHex = ($ilBytes | % { $_.ToString("X2") }) -join " "
            Write-Host "IL Bytes: $ilHex"
        } else {
            Write-Host "No method body (external/DLLImport?)"
        }
    } else {
        Write-Host "Method $mName not found"
    }
}
