$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload DLLs
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$files = Get-ChildItem -Path $clientPath | Where-Object { $_.Extension -eq ".dll" -or $_.Extension -eq ".exe" }
foreach ($f in $files) {
    Write-Host "Scanning: $($f.Name)"
    try {
        $asm = [System.Reflection.Assembly]::LoadFile($f.FullName)
        $types = @()
        try {
            $types = $asm.GetTypes()
        } catch [System.Reflection.ReflectionTypeLoadException] {
            Write-Host "  ReflectionTypeLoadException caught, examining loaded types..."
            $types = $_.Exception.Types | Where-Object { $_ -ne $null }
        }
        
        $found = $false
        foreach ($t in $types) {
            if ($t.FullName -like "*BDeviceRelated*") {
                Write-Host "  >> FOUND: $($t.FullName)"
                $found = $true
            }
        }
        if (-not $found) {
            # Let's print type count
            Write-Host "  No match. Total types: $($types.Count)"
        }
    } catch {
        Write-Host "  Failed to load or scan: $_"
    }
}
