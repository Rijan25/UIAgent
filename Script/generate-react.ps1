param(
    [string]$Model = "",
    [Alias("Input")]
    [string]$IrInputPath = "ui_generation/generated/ir/generated_ir.json",
    [Alias("Output")]
    [string]$ReactOutputPath = "ui_generation/generated/react/generated_app.tsx",
    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\common.ps1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runContext = Start-ScriptRun -RepoRoot $repoRoot -RunName "generate-react"
try {
    $resolvedInput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $IrInputPath
    $uvArgs = @("run", "python", "ui_generation/cli/ir_to_react.py", "--input", $resolvedInput, "--log-level", $LogLevel)
    if ($Model) {
        $uvArgs += @("--model", $Model)
    }
    if ($ReactOutputPath) {
        $resolvedOutput = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $ReactOutputPath
        $uvArgs += @("--output", $resolvedOutput)
    }

    Invoke-UvCommand -RunContext $runContext -Arguments $uvArgs
}
finally {
    Stop-ScriptRun -RunContext $runContext
}
