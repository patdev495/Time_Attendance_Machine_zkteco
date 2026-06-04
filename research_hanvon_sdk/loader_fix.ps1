$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asmOp = [Reflection.Assembly]::LoadFile($HwDevOpPath)
$interfaceType = $asmOp.GetType("Hanvon.FaceID.IHWDevType")

if (-not $interfaceType) {
    Write-Host "IHWDevType not found."
    exit
}

$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
# Preload common DLLs in the folder to help resolve types
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    $dllName = $_.Name
    try {
        $asm = [Reflection.Assembly]::LoadFile($_.FullName)
        $types = @()
        try {
            $types = $asm.GetTypes()
        } catch [System.Reflection.ReflectionTypeLoadException] {
            $types = $_.Exception.Types | Where-Object { $_ -ne $null }
        }
        
        foreach ($t in $types) {
            if ($t.IsClass -and $interfaceType.IsAssignableFrom($t)) {
                try {
                    $instance = [System.Activator]::CreateInstance($t)
                    $pv = $t.GetProperty("ProtocolVersion").GetValue($instance, $null)
                    $name = $t.GetProperty("LocalizedDisplayStr").GetValue($instance, $null)
                    Write-Host "DLL: $dllName, Class: $($t.FullName), Name: $name, ProtocolVersion: $pv"
                } catch {
                    $msg = $_.Exception.Message
                    Write-Host "DLL: $dllName, Class (no ctor): $($t.FullName) - Error: $msg"
                }
            }
        }
    } catch {
        Write-Host "Error loading $dllName : $_"
    }
}
