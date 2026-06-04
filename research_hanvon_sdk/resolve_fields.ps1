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

$commonPath = Join-Path $clientPath "KMS.Common.dll"
$asm = [Reflection.Assembly]::LoadFile($commonPath)
$module = $asm.GetModules()[0]

$fields = @(0x040002E8, 0x040002ED, 0x040002EE, 0x040002F0, 0x040002F2)

foreach ($fToken in $fields) {
    try {
        $resolved = $module.ResolveMember($fToken)
        Write-Host "Token $($fToken.ToString('X8')): Name=$($resolved.Name), DeclaringType=$($resolved.DeclaringType.FullName), FieldType=$($resolved.FieldType.FullName)"
    } catch {
        Write-Host "Error for token $($fToken.ToString('X8')): $_"
    }
}
