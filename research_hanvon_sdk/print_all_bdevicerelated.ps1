$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}
try { [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe")) | Out-Null } catch {}

Write-Host "=== Loaded Assemblies in AppDomain ==="
[System.AppDomain]::CurrentDomain.GetAssemblies() | ForEach-Object {
    $asm = $_
    $types = @()
    try {
        $types = $asm.GetTypes()
    } catch [System.Reflection.ReflectionTypeLoadException] {
        $types = $_.Exception.Types | Where-Object { $_ -ne $null }
    }
    foreach ($t in $types) {
        if ($t.FullName -like "*BDeviceRelated*") {
            Write-Host "Found: $($t.FullName) in $($asm.Location) (Assembly: $($asm.FullName))"
        }
    }
}
