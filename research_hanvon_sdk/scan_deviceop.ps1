$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try {
        $asm = [Reflection.Assembly]::LoadFile($_.FullName)
        foreach ($t in $asm.GetTypes()) {
            if ($t.FullName -like "*DeviceOperation*") {
                Write-Host "$($_.Name): $($t.FullName)"
            }
        }
    } catch {
    }
}
