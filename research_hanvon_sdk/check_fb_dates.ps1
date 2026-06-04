$fbDllPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client\hwFirebirdSql.Data.FirebirdClient.dll"
[Reflection.Assembly]::LoadFile($fbDllPath) | Out-Null

$fbConnStr = "User=SYSDBA;Password=masterkey;Database=C:\Users\Admin\Documents\Hanvon\FaceAtt\Client\HWATT.GDB;DataSource=127.0.0.1;Port=3050;Dialect=3;Charset=UTF8;"
$fbConn = New-Object FirebirdSql.Data.FirebirdClient.FbConnection($fbConnStr)

try {
    $fbConn.Open()
    
    # 1. Find DEVID for 192.168.209.61
    $cmd = $fbConn.CreateCommand()
    $cmd.CommandText = "SELECT DEVID, DEVNAME, IPADDRESS FROM KQZ_DEVINFO"
    $reader = $cmd.ExecuteReader()
    $devid = $null
    while ($reader.Read()) {
        $ip = $reader.GetString(2).Trim()
        Write-Host "Device: ID=$($reader.GetInt64(0)), Name=$($reader.GetString(1)), IP=$ip"
        if ($ip -eq "192.168.209.61") {
            $devid = $reader.GetInt64(0)
        }
    }
    $reader.Close()
    
    if ($devid -ne $null) {
        Write-Host "Found DEVID for 192.168.209.61: $devid"
        
        # 2. Query stats for this DEVID
        $statsCmd = $fbConn.CreateCommand()
        $statsCmd.CommandText = "SELECT MIN(CARDTIME), MAX(CARDTIME), COUNT(*) FROM KQZ_CARD WHERE DEVID = $devid"
        $statsReader = $statsCmd.ExecuteReader()
        if ($statsReader.Read()) {
            if (-not $statsReader.IsDBNull(0)) {
                $minDate = $statsReader.GetDateTime(0).ToString('yyyy-MM-dd HH:mm:ss')
                $maxDate = $statsReader.GetDateTime(1).ToString('yyyy-MM-dd HH:mm:ss')
                $count = $statsReader.GetInt32(2)
                Write-Host "KQZ_CARD stats for DEVID $devid :"
                Write-Host "  Min Date: $minDate"
                Write-Host "  Max Date: $maxDate"
                Write-Host "  Count   : $count"
            } else {
                Write-Host "No records in KQZ_CARD for DEVID=$devid"
            }
        }
        $statsReader.Close()
    } else {
        Write-Host "DEVID for 192.168.209.61 not found."
    }
} catch {
    Write-Host "Error: $_"
} finally {
    if ($fbConn.State -eq [System.Data.ConnectionState]::Open) { $fbConn.Close() }
}
