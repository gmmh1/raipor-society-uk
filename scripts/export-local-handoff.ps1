param(
    [string]$OutputFile = "docs/LOCAL_MODEL_SESSION_CONTEXT.md"
)

$ErrorActionPreference = "Stop"

function Get-CmdOutput {
    param([string]$Command)
    try {
        return (& pwsh -NoLogo -NoProfile -Command $Command | Out-String).Trim()
    } catch {
        return "(command failed: $Command)"
    }
}

$repoRoot = (Resolve-Path ".").Path

$branch = Get-CmdOutput "git rev-parse --abbrev-ref HEAD"
$head = Get-CmdOutput "git log -1 --oneline"
$status = Get-CmdOutput "git status --short --branch"
$recent = Get-CmdOutput "git log --oneline -n 8"
$staged = Get-CmdOutput "git diff --cached --name-only"
$unstaged = Get-CmdOutput "git diff --name-only"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"

$content = @"
# Local Model Session Context

Generated: $timestamp
Repository: $repoRoot
Branch: $branch
Head: $head

## Working tree status

~~~
$status
~~~

## Staged files

~~~
$staged
~~~

## Unstaged files

~~~
$unstaged
~~~

## Recent commits

~~~
$recent
~~~

## Required project rule files

Load these before implementation:
1. CLAUDE.md
2. docs/EXECUTABLE_PLAN.md
3. docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md
4. docs/QWEN_LOCAL_SYSTEM_PROMPT.md
5. docs/LOCAL_MODEL_CONTINUATION.md

## Notes for next local session

- Keep business logic in services/use-cases.
- Do not make unrelated file changes.
- Follow module order from docs/EXECUTABLE_PLAN.md.
"@

$dir = Split-Path -Parent $OutputFile
if (-not [string]::IsNullOrWhiteSpace($dir) -and -not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Set-Content -Path $OutputFile -Value $content -Encoding utf8
Write-Host "Wrote local handoff context to $OutputFile" -ForegroundColor Green
