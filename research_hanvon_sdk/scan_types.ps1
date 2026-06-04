$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)

Write-Host "Scanning types in FaceId.dll..."
foreach ($t in $asm.GetTypes()) {
    if ($t.Name -like "*Codec*" -or $t.Name -like "*Xor*" -or $t.Name -like "*SM4*" -or $t.FullName -like "*Security*") {
        Write-Host "Found type: $($t.FullName)"
    }
}
