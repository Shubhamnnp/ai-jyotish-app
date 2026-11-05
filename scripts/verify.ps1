# PowerShell Verification Script for JyotishOS (Phase U0, Task U0-T4)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

py -3 scripts/verify.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
