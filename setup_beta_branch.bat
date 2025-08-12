@echo off
echo Setting up Project Tracker Beta Branch...
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo Error: app.py not found. Please run this from the project_tracker directory.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Check git status
echo Checking git status...
git status
echo.

REM Create and switch to beta branch
echo Creating beta branch...
git checkout -b beta
echo.

REM Add all new beta files
echo Adding beta files to git...
git add .
echo.

REM Commit beta setup
echo Committing beta setup...
git commit -m "Beta setup: Add beta configuration and documentation

- Add beta_config.py with feature flags
- Add requirements-beta.txt with enhanced dependencies
- Add BETA_DEPLOYMENT.md with setup instructions
- Add README.md documenting beta features
- Update project structure for beta testing
- Add beta database support
- Add beta info route and template
- Update base template with beta indicators"
echo.

REM Show current branch
echo Current branch:
git branch
echo.

REM Show commit history
echo Recent commits:
git log --oneline -5
echo.

echo Beta branch setup complete!
echo.
echo Next steps:
echo 1. Push to remote: git push origin beta
echo 2. Install beta dependencies: pip install -r requirements-beta.txt
echo 3. Test beta features: python app.py
echo 4. Visit http://localhost:5000/beta to see beta info
echo.

pause
