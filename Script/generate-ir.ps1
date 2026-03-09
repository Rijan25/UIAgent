param(
    [string]$Model = "",
    [Alias("Output")]
    [string]$IrOutputPath = "ui_generation/generated/ir/generated_ir.json",
    [switch]$NoOverwrite,
    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runContext = Start-ScriptRun -RepoRoot $repoRoot -RunName "generate-ir"
try {
    $resolvedOutput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $IrOutputPath
    $uvArgs = @("run", "python", "ui_generation/cli/ir_generation.py", "--output", $resolvedOutput, "--log-level", $LogLevel)
    if ($Model) {
        $uvArgs += @("--model", $Model)
    }
    if ($NoOverwrite) {
        $uvArgs += "--no-overwrite"
    }

    Invoke-UvCommand -RunContext $runContext -Arguments $uvArgs
}
finally {
    Stop-ScriptRun -RunContext $runContext
}
