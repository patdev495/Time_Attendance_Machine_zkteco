# Load DLL
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($HwDevOpPath) | Out-Null

$msgTransfer = New-Object Hanvon.FaceID.MessageTransfered($false)

# Hex string from Wireshark
$hex = "4a1167415c45720e130917436d647225404650777c320c626172674545321a3b134150777d7c54620b1146716b734533421119267a7541335e5d173e2a320c62525c5869697e44620b1172617c5445365850504d66764f624c4e"

# Convert hex to bytes, then base64
$bytes = [byte[]]($hex -split '(?<=\G.{2})' | ? {$_} | % {[System.Convert]::ToByte($_, 16)})
$base64 = [System.Convert]::ToBase64String($bytes)

Write-Host "Base64 input to GetMessage: $base64"

# Attempt to decode
$decoded = $msgTransfer.GetMessage($base64)
Write-Host "Decoded message: $decoded"

# Test SetMessage encoding a typical handshake/command
$cmd = 'GetDeviceInfo()'
$encodedB64 = $msgTransfer.SetMessage($cmd)
$encodedBytes = [System.Convert]::FromBase64String($encodedB64)
$encodedHex = ($encodedBytes | % { $_.ToString("x2") }) -join ""
Write-Host "Encoded '$cmd' Hex: $encodedHex"
