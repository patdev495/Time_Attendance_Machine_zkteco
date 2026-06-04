$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
$asm = [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "KMS.Common.dll"))
foreach ($t in $asm.GetTypes()) {
    if ($t.Name -like "*BDeviceRelated*") {
        Write-Host "Name: $($t.Name)"
        Write-Host "FullName: $($t.FullName)"
    }
}
