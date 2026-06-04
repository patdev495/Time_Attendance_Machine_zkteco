$fbDllPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\hwFirebirdSql.Data.FirebirdClient.dll"
[Reflection.Assembly]::LoadFile($fbDllPath) | Out-Null

$fbConnStr = "User=SYSDBA;Password=masterkey;Database=C:\Users\Admin\Documents\Hanvon\FaceAtt\Client\HWATT.GDB;DataSource=127.0.0.1;Port=3050;Dialect=3;Charset=UTF8;"
$fbConn = New-Object FirebirdSql.Data.FirebirdClient.FbConnection($fbConnStr)

try {
    $fbConn.Open()
    $cmd = $fbConn.CreateCommand()
    $cmd.CommandText = @"
SELECT 
    TRIM(rf.RDB`$FIELD_NAME) AS COLUMN_NAME
FROM RDB`$RELATION_FIELDS rf
WHERE rf.RDB`$RELATION_NAME = 'KQZ_CARD'
ORDER BY rf.RDB`$FIELD_POSITION
"@

    $reader = $cmd.ExecuteReader()
    Write-Host "Columns in KQZ_CARD:"
    while ($reader.Read()) {
        Write-Host " - $($reader.GetString(0))"
    }
    $reader.Close()
} catch {
    Write-Host "Error: $_"
} finally {
    if ($fbConn.State -eq [System.Data.ConnectionState]::Open) { $fbConn.Close() }
}
