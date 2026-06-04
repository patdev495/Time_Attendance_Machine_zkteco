$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}
try { [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe")) | Out-Null } catch {}

Write-Host "=== Trace Assemblies and BDeviceRelated ==="
[System.AppDomain]::CurrentDomain.GetAssemblies() | ForEach-Object {
    $asm = $_
    $types = @()
    $hasType = $false
    try {
        $types = $asm.GetTypes()
    } catch [System.Reflection.ReflectionTypeLoadException] {
        $types = $_.Exception.Types | Where-Object { $_ -ne $null }
    }
    
    $matches = $types | Where-Object { $_.FullName -like "*BDeviceRelated*" }
    if ($matches) {
        Write-Host "Assembly: $($asm.FullName)"
        Write-Host "  Location: $($asm.Location)"
        Write-Host "  Types matching BDeviceRelated:"
        foreach ($m in $matches) {
            Write-Host "    - $($m.FullName)"
        }
    }
}
