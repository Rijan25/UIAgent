param(
    [string]$Model = "",
    [string]$IrOutput = "",
    [string]$ReactInput = "",
    [string]$ReactOutput = "",
    [string]$FrontendDir = "",
    [switch]$NoServe,
    [switch]$NoOverwrite,
    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runContext = Start-ScriptRun -RepoRoot $repoRoot -RunName "run-pipeline"
try {
    $uvArgs = @("run", "python", "main.py", "--log-level", $LogLevel)
    if ($Model) {
        $uvArgs += @("--model", $Model)
    }
    if ($IrOutput) {
        $resolvedIrOutput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $IrOutput
        $uvArgs += @("--ir-output", $resolvedIrOutput)
    }
    if ($ReactInput) {
        $resolvedReactInput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $ReactInput
        $uvArgs += @("--react-input", $resolvedReactInput)
    }
    if ($ReactOutput) {
        $resolvedReactOutput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $ReactOutput
        $uvArgs += @("--react-output", $resolvedReactOutput)
    }
    if ($FrontendDir) {
        $resolvedFrontendDir = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $FrontendDir
        $uvArgs += @("--frontend-dir", $resolvedFrontendDir)
    }
    if ($NoServe) {
        $uvArgs += "--no-serve"
    }
    if ($NoOverwrite) {
        $uvArgs += "--no-overwrite"
    }

    Invoke-UvCommand -RunContext $runContext -Arguments $uvArgs
}
finally {
    Stop-ScriptRun -RunContext $runContext
}
