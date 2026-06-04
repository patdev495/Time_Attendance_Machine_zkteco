$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)
$type = $asm.GetType("Com.FirstSolver.Splash.FaceId")

Write-Host "--- Fields in FaceId ---"
$type.GetFields([System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Static) | ForEach-Object {
    Write-Host "$($_.FieldType.Name) $($_.Name)"
}

Write-Host "`n--- Methods in FaceId ---"
$type.GetMethods([System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance) | ForEach-Object {
    $params = $_.GetParameters() | % { "$($_.ParameterType.Name) $($_.Name)" }
    Write-Host "$($_.ReturnType.Name) $($_.Name)($($params -join ', '))"
}
