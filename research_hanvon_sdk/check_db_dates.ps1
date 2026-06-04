# Query database to find record dates
$query = "SELECT MIN(OPTIME) as MinDate, MAX(OPTIME) as MaxDate, COUNT(*) as Total FROM test_hanvon.dbo.KQZ_CARD"

$connectionString = "Server=localhost;Database=test_hanvon;Trusted_Connection=True;"
if ($env:COMPUTERNAME -eq "Admin-PC" -or $true) {
    # Try typical SQL Server connection
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection
        $connection.ConnectionString = $connectionString
        $connection.Open()
        
        $command = $connection.CreateCommand()
        $command.CommandText = $query
        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($command)
        $dataset = New-Object System.Data.DataSet
        $adapter.Fill($dataset) | Out-Null
        
        $row = $dataset.Tables[0].Rows[0]
        Write-Host "Local Database KQZ_CARD statistics:"
        Write-Host "  Min Date  : $($row['MinDate'])"
        Write-Host "  Max Date  : $($row['MaxDate'])"
        Write-Host "  Total Logs: $($row['Total'])"
        
        $connection.Close()
    } catch {
        Write-Host "Error connecting to SQL Server: $_"
    }
}
