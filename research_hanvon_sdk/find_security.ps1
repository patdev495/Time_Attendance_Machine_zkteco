$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$asm = [Reflection.Assembly]::LoadFile($FaceIdPath)

$isecurityType = $asm.GetType("Com.FirstSolver.Splash.ISecurity")
if ($isecurityType) {
    Write-Host "Found ISecurity interface. Finding implementations..."
    foreach ($t in $asm.GetTypes()) {
        if ($t.IsClass -and $isecurityType.IsAssignableFrom($t)) {
            Write-Host "Class implementing ISecurity: $($t.FullName)"
            $constructors = $t.GetConstructors()
            foreach ($c in $constructors) {
                $params = $c.GetParameters() | % { "$($_.ParameterType.Name) $($_.Name)" }
                Write-Host "  Constructor: new($($params -join ', '))"
            }
        }
    }
} else {
    Write-Host "ISecurity type not found."
}
