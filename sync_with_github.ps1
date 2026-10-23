# Get GitHub history + add only your updated files (robocopy method)
# Run in PowerShell from this folder: .\sync_with_github.ps1
#
# What this does:
# 1. Clones the repo (with full history) to a temp folder
# 2. Copies YOUR current files over the clone with robocopy (keeps clone's .git)
# 3. You then add/commit only changes in the clone and push
#
# After running, do the commit in the clone folder (see Step 3 below).

$RepoUrl = "https://github.com/Neeraj-Bodinapalli/Agri-guide.git"
$CurrentDir = $PSScriptRoot
$CloneDir = Join-Path $env:TEMP "Agri-guide-clone"

Write-Host "Step 1: Cloning repo (with history) to $CloneDir ..."
if (Test-Path $CloneDir) { Remove-Item $CloneDir -Recurse -Force }
git clone $RepoUrl $CloneDir
if ($LASTEXITCODE -ne 0) { Write-Error "Clone failed"; exit 1 }

Write-Host "Step 2: Copying your files over the clone (robocopy) ..."
# /MIR would mirror (delete in dest); we use /E to copy subdirs but not delete
# /XD to exclude .git so we keep the clone's history
robocopy $CurrentDir $CloneDir /E /XD .git node_modules venv __pycache__ vector_db /NFL /NDL /NJH /NJS /NC /NS
if ($LASTEXITCODE -ge 8) { Write-Error "Robocopy failed"; exit 1 }

Write-Host "Step 3: Open the clone and commit only changes:"
Write-Host "   cd $CloneDir"
Write-Host "   git status"
Write-Host "   git add .    # or add only specific files"
Write-Host "   git commit -m \"Your message\""
Write-Host "   git push origin main"
Write-Host ""
Write-Host "Clone is at: $CloneDir"
