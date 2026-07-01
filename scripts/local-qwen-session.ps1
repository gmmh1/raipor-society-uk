param(
    [string]$HandoffFile = "docs/LOCAL_MODEL_SESSION_CONTEXT.md",
    [string]$OutputFile = "docs/LOCAL_MODEL_START_PROMPT.md",
    [switch]$OpenInEditor
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Push-Location $repoRoot

try {
    & pwsh -File "scripts/export-local-handoff.ps1" -OutputFile $HandoffFile | Out-Null

    $systemPromptPath = "docs/QWEN_LOCAL_SYSTEM_PROMPT.md"
    if (-not (Test-Path $systemPromptPath)) {
        throw "Missing required file: $systemPromptPath"
    }

    if (-not (Test-Path $HandoffFile)) {
        throw "Missing required file: $HandoffFile"
    }

    $systemPrompt = Get-Content -Path $systemPromptPath -Raw
    $handoff = Get-Content -Path $HandoffFile -Raw

    $starter = @"
# Qwen Session Starter Prompt

Use the text below as your first prompt to a local model (for example, Qwen2.5-Coder).

~~~text
Continue implementation in this repository with strict adherence to project architecture and governance constraints.

You must read and follow these files first:
- CLAUDE.md
- docs/EXECUTABLE_PLAN.md
- docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md
- docs/QWEN_LOCAL_SYSTEM_PROMPT.md
- docs/LOCAL_MODEL_SESSION_CONTEXT.md

Execution requirements:
- Implement the smallest safe patch.
- Keep business logic in use-cases/services.
- Add/update tests for changed behavior.
- Update docs for operational or behavior changes.
- Avoid unrelated file changes.

Response format:
1) Objective
2) Architecture decision
3) Files changed
4) Implementation
5) Tests
6) Documentation update
7) Future considerations
~~~

## System Prompt Reference

$systemPrompt

## Current Session Context

$handoff
"@

    $outDir = Split-Path -Parent $OutputFile
    if (-not [string]::IsNullOrWhiteSpace($outDir) -and -not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }

    Set-Content -Path $OutputFile -Value $starter -Encoding utf8
    Write-Host "Wrote Qwen starter prompt to $OutputFile" -ForegroundColor Green

    if ($OpenInEditor) {
        if (Get-Command code -ErrorAction SilentlyContinue) {
            code $OutputFile | Out-Null
        } else {
            Write-Host "VS Code CLI 'code' not found; skipped auto-open." -ForegroundColor Yellow
        }
    }
}
finally {
    Pop-Location
}
