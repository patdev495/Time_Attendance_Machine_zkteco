$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

Write-Host "=== Searching DLLs and EXEs for BDeviceRelated ==="
Get-ChildItem -Path $clientPath | Where-Object { $_.Extension -eq ".dll" -or $_.Extension -eq ".exe" } | ForEach-Object {
    $file = $_.FullName
    $name = $_.Name
    try {
        $asm = [System.Reflection.Assembly]::LoadFile($file)
        $types = @()
        try {
            $types = $asm.GetTypes()
        } catch [System.Reflection.ReflectionTypeLoadException] {
            $types = $_.Exception.Types | Where-Object { $_ -ne $null }
        }
        foreach ($t in $types) {
            if ($t.FullName -like "*BDeviceRelated*") {
                Write-Host "Found in: $name -> $($t.FullName)"
            }
        }
    } catch {
        Write-Host "Error scanning $name"
    }
}
