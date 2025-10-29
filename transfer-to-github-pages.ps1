<#
transfer-to-github-pages.ps1

Usage (run from this repository root in PowerShell):
  # Dry-run, shows what would change
  .\transfer-to-github-pages.ps1 -RepoUrl "https://github.com/Lokwo12/Lokwo12.github.io.git" -DryRun

  # Actual sync (prompts before deleting target files)
  .\transfer-to-github-pages.ps1 -RepoUrl "https://github.com/Lokwo12/Lokwo12.github.io.git" -Confirm

  # Force without prompt
  .\transfer-to-github-pages.ps1 -RepoUrl "https://github.com/Lokwo12/Lokwo12.github.io.git" -Force

Notes:
 - This script will clone the target repo into a temp folder, create a backup branch on the target containing the current state, mirror this repository's files into the target (excluding .git, .github, virtual env folders), then commit & push.
 - You must have 'git' available and authenticated to GitHub (SSH key or credential helper).
 - Review DryRun output before performing the live sync.
 - The script will NOT change this repository. It overwrites the contents of the target repo.
#>
param(
    [string]$RepoUrl = "https://github.com/Lokwo12/Lokwo12.github.io.git",
    [string]$TempDir = "$env:TEMP\lokwo-pages-transfer",
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Confirm
)

function Write-Info { param($m) Write-Host "[info] $m" -ForegroundColor Cyan }
function Write-Warn { param($m) Write-Host "[warn] $m" -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host "[error] $m" -ForegroundColor Red }

# Ensure git exists
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Err "git is not installed or not on PATH. Install git before running this script."; exit 1
}

$Source = (Get-Location).Path
Write-Info "Source repo: $Source"
Write-Info "Target repo: $RepoUrl"
Write-Info "Working temp dir: $TempDir"

# Confirm action when not dry-run
if (-not $DryRun -and -not $Force -and -not $Confirm) {
    Write-Warn "This will overwrite the contents of the target repository when you run for real. Use -DryRun to preview, -Confirm to proceed (prompts), or -Force to run without prompt."
    $answer = Read-Host "Proceed with dry-run? (y to continue with dry-run, n to cancel)"
    if ($answer -ne 'y') { Write-Info "Cancelled by user."; exit 0 }
}

# Prepare temp dir
if (Test-Path $TempDir) {
    Write-Info "Removing existing temp dir: $TempDir"
    Remove-Item -Recurse -Force -LiteralPath $TempDir
}
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Clone target
Write-Info "Cloning target repository..."
$clone = git clone $RepoUrl $TempDir 2>&1
if ($LASTEXITCODE -ne 0) { Write-Err "git clone failed: $clone"; exit 1 }

# Make sure we have a named branch (assume main or master)
Push-Location $TempDir
try {
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if (-not $branch) { $branch = 'main' }
    Write-Info "Target default branch: $branch"

    # Create a backup branch on remote
    $timestamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
    $backupBranch = "backup-before-sync-$timestamp"
    Write-Info "Creating backup branch '$backupBranch' on target repo"
    git checkout -b $backupBranch 2>&1 | Out-Null
    git push origin $backupBranch 2>&1 | Out-Null
    # Switch back
    git checkout $branch 2>&1 | Out-Null

    # Prepare destination: remove all files except .git
    Write-Info "Cleaning target working tree (preserving .git)"
    Get-ChildItem -Force -LiteralPath $TempDir | Where-Object { $_.Name -ne '.git' } | ForEach-Object { Remove-Item -Recurse -Force -LiteralPath $_.FullName }

    # Copy files from source into temp (exclude .git and common virtual env dirs)
    $excludes = @('.git', '.github', 'venv', '.venv', 'env', 'node_modules')
    Write-Info "Copying files from source to target (excludes: $($excludes -join ', '))"

    if ($DryRun) {
        Write-Info "DRY RUN: showing what would be copied"
        Get-ChildItem -Recurse -Force -LiteralPath $Source | Where-Object { ($excludes -notcontains $_.Name) -and ($_.FullName -notlike "$TempDir*") } | Select-Object -First 50 | ForEach-Object { Write-Host $_.FullName }
        Write-Info "DRY RUN complete. No changes were made to target repo."
        Pop-Location
        exit 0
    }

    # Use robocopy for robust Windows copy; mirror source into temp while excluding directories
    $robocopyExcludes = $excludes -join ' '
    # Build robocopy exclude switches for directories (/XD) and files (/XF empty here)
    $xdArgs = $excludes | ForEach-Object { "/XD `"$Source\\$_`"" } | Out-String
    # Simpler invocation: use robocopy with /MIR and /XD from Source to Temp
    $xdParams = $excludes | ForEach-Object { "/XD `"$_`"" } | Out-String

    # Run robocopy
    $robocopyCmd = "robocopy `"$Source`" `"$TempDir`" /MIR /XD $($excludes -join ' ') /NFL /NDL /NJH /NJS"
    Write-Info "Running: $robocopyCmd"
    $rc = robocopy $Source $TempDir /MIR /XD $excludes 2>&1
    $robocopyExit = $LASTEXITCODE
    if ($robocopyExit -ge 8) { Write-Warn "robocopy reported an error (exit code $robocopyExit). Please inspect output." }

    # Git add/commit/push if there are changes
    git add -A 2>&1 | Out-Null
    $status = git status --porcelain
    if (-not $status) {
        Write-Info "No changes detected in target repository after copy. Nothing to commit."
        Pop-Location
        exit 0
    }

    git commit -m "Sync from Lokwo_Denis_Portfolio on $timestamp" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "git commit failed. Check the repo in $TempDir"
        Pop-Location
        exit 1
    }

    Write-Info "Pushing changes to remote (branch: $branch)"
    git push origin $branch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Err "git push failed. Check authentication and remote permissions."; Pop-Location; exit 1 }

    Write-Info "Sync complete. Target repository updated and a backup branch '$backupBranch' was created."
}
finally {
    Pop-Location
}
