$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)
$xorType = $asm.GetType("Com.FirstSolver.Splash.Xor64Codec")

# Case 1: SecretKey = "123"
$xor1 = [System.Activator]::CreateInstance($xorType)
$xorType.GetProperty("SecretKey").SetValue($xor1, "123", $null)
$derivedKey1 = $xorType.GetField("DerivedKey", [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance).GetValue($xor1)
$hex1 = ($derivedKey1 | % { $_.ToString("X2") }) -join " "
Write-Host "DerivedKey for '123': $hex1"

# Case 2: SecretKey = ""
$xor2 = [System.Activator]::CreateInstance($xorType)
$xorType.GetProperty("SecretKey").SetValue($xor2, "", $null)
$derivedKey2 = $xorType.GetField("DerivedKey", [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance).GetValue($xor2)
$hex2 = ($derivedKey2 | % { $_.ToString("X2") }) -join " "
Write-Host "DerivedKey for '': $hex2"
