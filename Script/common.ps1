Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Start-ScriptRun {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,
        [Parameter(Mandatory = $true)]
        [string]$RunName
    )

    $startTime = Get-Date
    $timestamp = $startTime.ToString("yyyyMMdd-HHmmss")
    $scriptLogDir = Join-Path $RepoRoot "ui_generation\logs\scripts"
    New-Item -ItemType Directory -Path $scriptLogDir -Force | Out-Null
    $transcriptPath = Join-Path $scriptLogDir "$RunName-$timestamp.log"
    Start-Transcript -Path $transcriptPath | Out-Null

    return @{
        RepoRoot = $RepoRoot
        RunName = $RunName
        StartTime = $startTime
        ScriptLogDir = $scriptLogDir
        TranscriptPath = $transcriptPath
    }
}

function Invoke-UvCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$RunContext,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Push-Location $RunContext.RepoRoot
    try {
        & uv @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$($RunContext.RunName) failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

function Resolve-RepoPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,
        [Parameter(Mandatory = $true)]
        [string]$PathValue
    )

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathValue))
}

function Trim-ScriptLogs {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$LogDir,
        [int]$KeepLatest = 20
    )

    $logs = Get-ChildItem -Path $LogDir -Filter "*.log" -File | Sort-Object LastWriteTime -Descending
    if ($logs.Count -le $KeepLatest) {
        return
    }

    $logsToDelete = $logs | Select-Object -Skip $KeepLatest
    foreach ($log in $logsToDelete) {
        Remove-Item -Path $log.FullName -Force
    }
}

function Stop-ScriptRun {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$RunContext
    )

    Stop-Transcript | Out-Null
    Trim-ScriptLogs -LogDir $RunContext.ScriptLogDir
    $endTime = Get-Date
    $elapsed = ($endTime - $RunContext.StartTime).TotalSeconds
    Write-Host ("{0} finished in {1:N2}s. Transcript: {2}" -f $RunContext.RunName, $elapsed, $RunContext.TranscriptPath)
}
