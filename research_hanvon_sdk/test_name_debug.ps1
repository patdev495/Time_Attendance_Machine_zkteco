$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$asm = [System.Reflection.Assembly]::LoadFile("C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll")
foreach ($t in $asm.GetTypes()) {
    if ($t.FullName -like "*BDeviceRelated*") {
        Write-Host "FullName: '$($t.FullName)'"
        Write-Host "AssemblyQualifiedName: '$($t.AssemblyQualifiedName)'"
    }
}
