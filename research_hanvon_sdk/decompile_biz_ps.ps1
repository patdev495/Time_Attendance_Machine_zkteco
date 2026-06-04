$clientPath = "C:\Program Files (x86)\Hanvon\FaceAtt\Client"
[System.IO.Directory]::SetCurrentDirectory($clientPath)
Push-Location $clientPath

# Preload dependencies
Get-ChildItem -Path $clientPath -Filter "*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFile($_.FullName) | Out-Null } catch {}
}
try { [System.Reflection.Assembly]::LoadFile((Join-Path $clientPath "mca.exe")) | Out-Null } catch {}

# Find BDeviceRelated in the AppDomain
$type = $null
[System.AppDomain]::CurrentDomain.GetAssemblies() | ForEach-Object {
    $asm = $_
    $types = @()
    try {
        $types = $asm.GetTypes()
    } catch [System.Reflection.ReflectionTypeLoadException] {
        $types = $_.Exception.Types | Where-Object { $_ -ne $null }
    }
    
    foreach ($t in $types) {
        if ($t.FullName -eq "Hanvon.KMS.Business.BDeviceRelated") {
            $type = $t
        }
    }
}

if (-not $type) {
    Write-Host "FAILED: Type Hanvon.KMS.Business.BDeviceRelated not found in AppDomain."
    exit
}

Write-Host "Found Type: $($type.FullName)"
Write-Host "Assembly Location: $($type.Assembly.Location)"

# Define Helper function to dump method body
function Dump-Method($method) {
    if (-not $method) {
        Write-Host "Method not found."
        return
    }
    
    Write-Host "`n=== Disassembling $($method.DeclaringType.FullName).$($method.Name) ==="
    foreach ($p in $method.GetParameters()) {
        Write-Host "  Param: $($p.ParameterType.Name) $($p.Name)"
    }
    
    $body = $method.GetMethodBody()
    if (-not $body) {
        Write-Host "No method body"
        return
    }
    
    $il = $body.GetILAsByteArray()
    $pos = 0
    
    # We load OpCodes using reflection
    $opCodes = @{}
    [System.Reflection.Emit.OpCodes].GetFields([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Static) | ForEach-Object {
        $op = $_.GetValue($null)
        $opCodes[$op.Value] = $op
    }
    
    while ($pos -lt $il.Length) {
        $offset = $pos
        $opByte = $il[$pos++]
        $op = $null
        
        if ($opByte -eq 0xFE) {
            if ($pos -ge $il.Length) { break }
            $opByte2 = $il[$pos++]
            $val = [int](0xFE00 -bor $opByte2)
            $op = $opCodes[$val]
        } else {
            $op = $opCodes[[int]$opByte]
        }
        
        if (-not $op) {
            Write-Host "  IL_$($offset.ToString('X4')): Unknown Opcode $opByte"
            continue
        }
        
        $operand = ""
        $opType = $op.OperandType.ToString()
        
        switch ($opType) {
            "InlineNone" { }
            "ShortInlineI" {
                $operand = $il[$pos++].ToString("X2")
            }
            "ShortInlineVar" {
                $operand = $il[$pos++].ToString("X2")
            }
            "InlineVar" {
                $val = [System.BitConverter]::ToUInt16($il, $pos)
                $operand = $val.ToString("X4")
                $pos += 2
            }
            "InlineI" {
                $val = [System.BitConverter]::ToInt32($il, $pos)
                $operand = $val.ToString("X8")
                $pos += 4
            }
            "ShortInlineR" {
                $val = [System.BitConverter]::ToInt32($il, $pos)
                $operand = $val.ToString("X8")
                $pos += 4
            }
            "InlineI8" {
                $val = [System.BitConverter]::ToInt64($il, $pos)
                $operand = $val.ToString("X16")
                $pos += 8
            }
            "InlineR" {
                $val = [System.BitConverter]::ToInt64($il, $pos)
                $operand = $val.ToString("X16")
                $pos += 8
            }
            "InlineBrTarget" {
                $val = [System.BitConverter]::ToInt32($il, $pos)
                $target = $offset + 5 + $val
                $operand = "offset " + $target.ToString("X4")
                $pos += 4
            }
            "ShortInlineBrTarget" {
                $b = $il[$pos++]
                if ($b -gt 127) { $val = $b - 256 } else { $val = $b }
                $target = $offset + 2 + $val
                $operand = "offset " + $target.ToString("X4")
            }
            { $_ -in @("InlineField", "InlineMethod", "InlineTok", "InlineType") } {
                $token = [System.BitConverter]::ToInt32($il, $pos)
                $operand = "token " + $token.ToString("X8")
                try {
                    $member = $method.Module.ResolveMember($token)
                    $operand += " ($($member.Name))"
                } catch {}
                $pos += 4; break
            }
            "InlineString" {
                $token = [System.BitConverter]::ToInt32($il, $pos)
                $operand = "string token " + $token.ToString("X8")
                try {
                    $str = $method.Module.ResolveString($token)
                    $operand += " ($str)"
                } catch {}
                $pos += 4
            }
            Default {
                # Skip operand size based on type if unknown
            }
        }
        
        Write-Host ("  IL_{0:X4}: {1,-10} {2}" -f $offset, $op.Name, $operand)
    }
}

# Dump methods
$methodsToDump = @("DownRcdAndSave", "AutoSyncRcd", "AutoDownRcdAndSave", "ClearRcd")
foreach ($mName in $methodsToDump) {
    $m = $type.GetMethod($mName, [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::Instance)
    Dump-Method $m
}
