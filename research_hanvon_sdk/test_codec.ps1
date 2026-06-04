$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)

# Raw Hex data of packet payload (skipping the first 4 bytes of length header)
# Payload length = 90 bytes (0x0000005a -> 90 bytes)
# The full data is: 0000005a4a1167415c45720e130917436d647225404650777c320c626172674545321a3b134150777d7c54620b1146716b734533421119267a7541335e5d173e2a320c62525c5869697e44620b1172617c5445365850504d66764f624c4e
# The payload is starting from 4a11...

$hex = "4a1167415c45720e130917436d647225404650777c320c626172674545321a3b134150777d7c54620b1146716b734533421119267a7541335e5d173e2a320c62525c5869697e44620b1172617c5445365850504d66764f624c4e"
$payloadBytes = [byte[]]($hex -split '(?<=\G.{2})' | ? {$_} | % {[System.Convert]::ToByte($_, 16)})

# Test Xor64Codec
Write-Host "--- Test Xor64Codec (SecretKey = 123) ---"
$xor = New-Object Com.FirstSolver.Splash.Xor64Codec
$xor.SecretKey = "123"
try {
    $decrypted = $xor.Decode($payloadBytes, 0, $payloadBytes.Length)
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "Xor64 (123) Decrypted UTF8: $text"
} catch {
    Write-Host "Xor64 (123) Error: $_"
}

# Test SM4Codec
Write-Host "`n--- Test SM4Codec (SecretKey = 123) ---"
$sm4 = New-Object Com.FirstSolver.Splash.SM4Codec
$sm4.SecretKey = "123"
try {
    $decrypted = $sm4.Decode($payloadBytes, 0, $payloadBytes.Length)
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "SM4 (123) Decrypted UTF8: $text"
} catch {
    Write-Host "SM4 (123) Error: $_"
}

# Try empty SecretKey
Write-Host "`n--- Test Xor64Codec (SecretKey = '') ---"
$xor2 = New-Object Com.FirstSolver.Splash.Xor64Codec
$xor2.SecretKey = ""
try {
    $decrypted = $xor2.Decode($payloadBytes, 0, $payloadBytes.Length)
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "Xor64 ('') Decrypted UTF8: $text"
} catch {
    Write-Host "Xor64 ('') Error: $_"
}

# Try SM4Codec with empty SecretKey
Write-Host "`n--- Test SM4Codec (SecretKey = '') ---"
$sm4_2 = New-Object Com.FirstSolver.Splash.SM4Codec
$sm4_2.SecretKey = ""
try {
    $decrypted = $sm4_2.Decode($payloadBytes, 0, $payloadBytes.Length)
    $text = [System.Text.Encoding]::UTF8.GetString($decrypted)
    Write-Host "SM4 ('') Decrypted UTF8: $text"
} catch {
    Write-Host "SM4 ('') Error: $_"
}
