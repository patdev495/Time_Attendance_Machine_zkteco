$fbDllPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\hwFirebirdSql.Data.FirebirdClient.dll"
[Reflection.Assembly]::LoadFile($fbDllPath) | Out-Null

$fbConnStr = "User=SYSDBA;Password=masterkey;Database=C:\Users\Admin\Documents\Hanvon\FaceAtt\Client\HWATT.GDB;DataSource=127.0.0.1;Port=3050;Dialect=3;Charset=UTF8;"
$fbConn = New-Object FirebirdSql.Data.FirebirdClient.FbConnection($fbConnStr)

try {
    $fbConn.Open()
    $cmd = $fbConn.CreateCommand()
    $cmd.CommandText = "SELECT * FROM KQZ_DEVINFO WHERE IPADDRESS = '192.168.209.61'"
    $reader = $cmd.ExecuteReader()
    
    $schemaTable = $reader.GetSchemaTable()
    $columns = @()
    foreach ($row in $schemaTable.Rows) {
        $columns += $row["ColumnName"]
    }
    
    while ($reader.Read()) {
        Write-Host "=== Device Database Config ==="
        for ($i = 0; $i -lt $reader.FieldCount; $i++) {
            $colName = $columns[$i]
            $val = $reader.GetValue($i)
            Write-Host "$colName : $val"
        }
    }
    $reader.Close()
} catch {
    Write-Host "Error: $_"
} finally {
    if ($fbConn.State -eq [System.Data.ConnectionState]::Open) { $fbConn.Close() }
}
