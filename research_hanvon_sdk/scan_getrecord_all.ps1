$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try {
        $asm = [Reflection.Assembly]::LoadFile($_.FullName)
        foreach ($t in $asm.GetTypes()) {
            if ($t.FullName -like "*GetRecord*") {
                Write-Host "$($_.Name): $($t.FullName)"
                Write-Host "  Properties:"
                $t.GetProperties() | % { Write-Host "    $($_.PropertyType.Name) $($_.Name)" }
                Write-Host "  Fields:"
                $t.GetFields() | % { Write-Host "    $($_.FieldType.Name) $($_.Name)" }
            }
        }
    } catch {
    }
}
