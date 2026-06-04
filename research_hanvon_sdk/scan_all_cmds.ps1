$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
# Preload common DLLs
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$KMSCommonPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll"
$asm = [Reflection.Assembly]::LoadFile($KMSCommonPath)

Write-Host "Scanning command types..."
$types = @()
try {
    $types = $asm.GetTypes()
} catch [System.Reflection.ReflectionTypeLoadException] {
    $types = $_.Exception.Types | Where-Object { $_ -ne $null }
}

foreach ($t in $types) {
    if ($t.IsClass -and ($t.Name -like "*Cmd" -or $t.Name -like "*CmdPar" -or $t.Name -like "*Par")) {
        try {
            $fields = $t.GetFields()
            if ($fields.Length -gt 0) {
                Write-Host "Type: $($t.FullName)"
                foreach ($f in $fields) {
                    Write-Host "  Field: $($f.FieldType.Name) $($f.Name)"
                }
            }
        } catch {}
    }
}
