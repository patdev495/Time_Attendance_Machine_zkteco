$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
$asm1 = [Reflection.Assembly]::LoadFile($FaceIdPath)
$asm2 = [Reflection.Assembly]::LoadFile($HwDevOpPath)

Write-Host "Scanning types in FaceId.dll..."
foreach ($t in $asm1.GetTypes()) {
    if ($t.FullName -like "*GetRecord*") {
        Write-Host "FaceId.dll: $($t.FullName)"
    }
}

Write-Host "Scanning types in HwDevOp.dll..."
foreach ($t in $asm2.GetTypes()) {
    if ($t.FullName -like "*GetRecord*") {
        Write-Host "HwDevOp.dll: $($t.FullName)"
    }
}
