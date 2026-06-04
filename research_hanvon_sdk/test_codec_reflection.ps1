# Explicitly load assemblies
$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [System.Reflection.Assembly]::LoadFile($FaceIdPath)

# Raw Hex data of packet payload (skipping the first 4 bytes of length header)
$hex = "4a1167415c45720e130917436d647225404650777c320c626172674545321a3b134150777d7c54620b1146716b734533421119267a7541335e5d173e2a320c62525c5869697e44620b1172617c5445365850504d66764f624c4e"
$payloadBytes = [byte[]]($hex -split '(?<=\G.{2})' | ? {$_} | % {[System.Convert]::ToByte($_, 16)})

# Instantiating through Assembly instance to ensure it gets the correct types
$xorType = $asm.GetType("Com.FirstSolver.Splash.Xor64Codec")
$sm4Type = $asm.GetType("Com.FirstSolver.Splash.SM4Codec")

Write-Host "--- Test Xor64Codec (SecretKey = 123) ---"
$xor = [System.Activator]::CreateInstance($xorType)
$xorType.GetProperty("SecretKey").SetValue($xor, "123", $null)
try {
    $decodeMethod = $xorType.GetMethod("Decode", [type[]]@([byte[]], [int], [int]))
    $decrypted = $decodeMethod.Invoke($xor, @($payloadBytes, 0, $payloadBytes.Length))
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "Xor64 (123) Decrypted UTF8: $text"
} catch {
    Write-Host "Xor64 (123) Error: $_"
    if ($_.InnerException) { Write-Host "Inner: $($_.InnerException.Message)" }
}

Write-Host "`n--- Test SM4Codec (SecretKey = 123) ---"
$sm4 = [System.Activator]::CreateInstance($sm4Type)
$sm4Type.GetProperty("SecretKey").SetValue($sm4, "123", $null)
try {
    $decodeMethod = $sm4Type.GetMethod("Decode", [type[]]@([byte[]], [int], [int]))
    $decrypted = $decodeMethod.Invoke($sm4, @($payloadBytes, 0, $payloadBytes.Length))
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "SM4 (123) Decrypted UTF8: $text"
} catch {
    Write-Host "SM4 (123) Error: $_"
    if ($_.InnerException) { Write-Host "Inner: $($_.InnerException.Message)" }
}

Write-Host "`n--- Test Xor64Codec (SecretKey = '') ---"
$xor2 = [System.Activator]::CreateInstance($xorType)
$xorType.GetProperty("SecretKey").SetValue($xor2, "", $null)
try {
    $decodeMethod = $xorType.GetMethod("Decode", [type[]]@([byte[]], [int], [int]))
    $decrypted = $decodeMethod.Invoke($xor2, @($payloadBytes, 0, $payloadBytes.Length))
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "Xor64 ('') Decrypted UTF8: $text"
} catch {
    Write-Host "Xor64 ('') Error: $_"
    if ($_.InnerException) { Write-Host "Inner: $($_.InnerException.Message)" }
}

Write-Host "`n--- Test SM4Codec (SecretKey = '') ---"
$sm4_2 = [System.Activator]::CreateInstance($sm4Type)
$sm4Type.GetProperty("SecretKey").SetValue($sm4_2, "", $null)
try {
    $decodeMethod = $sm4Type.GetMethod("Decode", [type[]]@([byte[]], [int], [int]))
    $decrypted = $decodeMethod.Invoke($sm4_2, @($payloadBytes, 0, $payloadBytes.Length))
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "SM4 ('') Decrypted UTF8: $text"
} catch {
    Write-Host "SM4 ('') Error: $_"
    if ($_.InnerException) { Write-Host "Inner: $($_.InnerException.Message)" }
}
