$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
$hwDevPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\hwDevice"

[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload assembly directories
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$commonPath = Join-Path $clientPath "KMS.Common.dll"
$asm = [Reflection.Assembly]::LoadFile($commonPath)

$tRecordPar = $asm.GetType("Hanvon.FaceID.RecordPar")
Write-Host "=== Hanvon.FaceID.RecordPar Fields ==="
foreach ($f in $tRecordPar.GetFields([System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic)) {
    Write-Host "$($f.Name) : $($f.FieldType.FullName)"
}

$tClientRtnPar = $asm.GetType("Hanvon.FaceID.ClientGetRecordRtnPar")
Write-Host "`n=== Hanvon.FaceID.ClientGetRecordRtnPar Fields ==="
foreach ($f in $tClientRtnPar.GetFields([System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic)) {
    Write-Host "$($f.Name) : $($f.FieldType.FullName)"
}
