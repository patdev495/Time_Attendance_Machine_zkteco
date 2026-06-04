$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)
$type = $asm.GetType("Com.FirstSolver.Splash.Xor64Codec")

# List all methods
Write-Host "--- Methods in Xor64Codec ---"
$methods = $type.GetMethods([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance)
foreach ($m in $methods) {
    if ($m.DeclaringType -eq $type) {
        $params = $m.GetParameters() | % { "$($_.ParameterType.Name) $($_.Name)" }
        Write-Host "$($m.ReturnType.Name) $($m.Name)($($params -join ', '))"
        $body = $m.GetMethodBody()
        if ($body) {
            $ilBytes = $body.GetILAsByteArray()
            $ilHex = ($ilBytes | % { $_.ToString("X2") }) -join " "
            Write-Host "  IL: $ilHex"
        }
    }
}

# List all fields
Write-Host "`n--- Fields in Xor64Codec ---"
$type.GetFields([System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Public) | ForEach-Object {
    Write-Host "$($_.FieldType.Name) $($_.Name)"
}
