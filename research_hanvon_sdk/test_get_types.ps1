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
Write-Host "Calling InitDevTypeDict..."
$initMethod.Invoke($null, @($hwDevPath, "HW__*.dll"))

$getSortedList = $refType.GetMethod("GetSortedDevTypeStrList")
$types = $getSortedList.Invoke($null, $null)
Write-Host "Types count: $($types.Count)"
foreach ($t in $types) {
    Write-Host "Type: $t"
}
