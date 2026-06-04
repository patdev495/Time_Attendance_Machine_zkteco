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

try {
    $resolved = $module.ResolveMember(0x2B000006)
    Write-Host "Resolved member 0x2B000006: $($resolved.DeclaringType.FullName).$($resolved.Name) (Type: $($resolved.GetType().Name))"
} catch {
    Write-Host "ResolveMember error: $_"
}

try {
    $resolvedMethod = $module.ResolveMethod(0x06000427) # ParseToRcdInfoListV2 token
    Write-Host "Resolved method 0x06000427: $($resolvedMethod.Name)"
} catch {
    Write-Host "ResolveMethod V2 error: $_"
}
