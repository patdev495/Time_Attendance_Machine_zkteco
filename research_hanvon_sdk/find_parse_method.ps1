$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
# Preload common DLLs
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}

$KMSCommonPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll"
$asm = [Reflection.Assembly]::LoadFile($KMSCommonPath)

$types = @()
try {
    $types = $asm.GetTypes()
} catch [System.Reflection.ReflectionTypeLoadException] {
    $types = $_.Exception.Types | Where-Object { $_ -ne $null }
}

foreach ($t in $types) {
    try {
        $methods = $t.GetMethods([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Static)
        foreach ($m in $methods) {
            if ($m.Name -like "*ParseToRcdInfoList*") {
                Write-Host "Found method in Class: $($t.FullName)"
                $params = $m.GetParameters() | % { "$($_.ParameterType.Name) $($_.Name)" }
                Write-Host "  Method: $($m.ReturnType.Name) $($m.Name)($($params -join ', '))"
            }
        }
    } catch {}
}
