$FaceIdPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll"
$HwDevOpPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll"
[Reflection.Assembly]::LoadFile($FaceIdPath) | Out-Null
$asm = [Reflection.Assembly]::LoadFile($HwDevOpPath)

$types = @(
    "Hanvon.FaceID.ClientGetRecordCmd",
    "Hanvon.FaceID.ClientGetRecordCmdPar",
    "Hanvon.FaceID.ClientGetRecord_RR",
    "Hanvon.FaceID.ClientGetRecordRtnPar"
)

foreach ($typeName in $types) {
    $t = $asm.GetType($typeName)
    if ($t) {
        Write-Host "========================================"
        Write-Host "Type: $($t.FullName)"
        Write-Host "========================================"
        
        Write-Host "Properties:"
        $t.GetProperties() | ForEach-Object {
            Write-Host "  $($_.PropertyType.Name) $($_.Name)"
        }
        
        Write-Host "Fields:"
        $t.GetFields() | ForEach-Object {
            Write-Host "  $($_.FieldType.Name) $($_.Name)"
        }
    } else {
        Write-Host "Type $typeName not found"
    }
}
