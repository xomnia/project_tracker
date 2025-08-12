Write-Host "Setting up Project Tracker Beta Branch..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "Error: app.py not found. Please run this from the project_tracker directory." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "Current directory: $PWD" -ForegroundColor Yellow
Write-Host ""

# Check git status
Write-Host "Checking git status..." -ForegroundColor Cyan
try {
    git status
} catch {
    Write-Host "Git command failed. Please ensure git is installed and in your PATH." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}
Write-Host ""

# Create and switch to beta branch
Write-Host "Creating beta branch..." -ForegroundColor Cyan
git checkout -b beta
Write-Host ""

# Add all new beta files
Write-Host "Adding beta files to git..." -ForegroundColor Cyan
git add .
Write-Host ""

# Commit beta setup
Write-Host "Committing beta setup..." -ForegroundColor Cyan
$commitMessage = @"
Beta setup: Add beta configuration and documentation

- Add beta_config.py with feature flags
- Add requirements-beta.txt with enhanced dependencies
- Add BETA_DEPLOYMENT.md with setup instructions
- Add README.md documenting beta features
- Update project structure for beta testing
- Add beta database support
- Add beta info route and template
- Update base template with beta indicators
"@

git commit -m $commitMessage
Write-Host ""

# Show current branch
Write-Host "Current branch:" -ForegroundColor Cyan
git branch
Write-Host ""

# Show commit history
Write-Host "Recent commits:" -ForegroundColor Cyan
git log --oneline -5
Write-Host ""

Write-Host "Beta branch setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Push to remote: git push origin beta"
Write-Host "2. Install beta dependencies: pip install -r requirements-beta.txt"
Write-Host "3. Test beta features: python app.py"
Write-Host "4. Visit http://localhost:5000/beta to see beta info"
Write-Host ""

Read-Host "Press Enter to continue"
