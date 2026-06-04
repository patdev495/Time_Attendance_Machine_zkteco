$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
$asm = [Reflection.Assembly]::LoadFile($HwDevOpPath)
$refType = $asm.GetType("Hanvon.FaceID.DevTypeReflection")

Write-Host "=== Fields ==="
foreach ($f in $refType.GetFields([System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance)) {
    Write-Host "Field: $($f.FieldType) $($f.Name)"
}

Write-Host "`n=== Methods ==="
foreach ($m in $refType.GetMethods([System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance)) {
    Write-Host "Method: $($m.Name)"
}
