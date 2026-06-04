$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
$files = Get-ChildItem -Path $clientPath | Where-Object { $_.Extension -eq ".dll" -or $_.Extension -eq ".exe" }

foreach ($f in $files) {
    $filePath = $f.FullName
    $fileName = $f.Name
    
    # Run a separate powershell process to load just this file and check its types
    $cmd = "[System.Reflection.Assembly]::LoadFile('$filePath').GetTypes() | Where-Object { `$_.FullName -like '*BDeviceRelated*' } | Select-Object -Property FullName"
    
    # We run C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe for 32-bit compatibility
    $result = & C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command "
        try {
            $cmd
        } catch [System.Reflection.ReflectionTypeLoadException] {
            `$_.Exception.Types | Where-Object { `$_ -ne `$null -and `$_.FullName -like '*BDeviceRelated*' } | Select-Object -Property FullName
        } catch {
            # Ignore other errors
        }
    "
    
    if ($result) {
        Write-Host "FOUND in: $fileName"
        Write-Host $result
    }
}
