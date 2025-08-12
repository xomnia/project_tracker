# Git Beta Branch Setup Guide

Since we couldn't execute git commands directly, here's how to set up your beta fork properly:

## 🔧 Manual Git Setup

### 1. Create Beta Branch

```bash
# Make sure you're in the project directory
cd /c/Users/xomni/OneDrive/Documents/webdev/project_tracker_beta/project_tracker

# Create and switch to beta branch
git checkout -b beta

# Verify you're on beta branch
git branch
```

### 2. Update Remote Configuration

```bash
# Add your beta repository as origin (if different from main)
git remote set-url origin https://github.com/xomnia/project_tracker_beta.git

# Add main repository as upstream
git remote add upstream https://github.com/xomnia/project_tracker.git

# Verify remotes
git remote -v
```

### 3. Commit Beta Changes

```bash
# Add all new beta files
git add .

# Commit beta setup
git commit -m "Beta setup: Add beta configuration and documentation

- Add beta_config.py with feature flags
- Add requirements-beta.txt with enhanced dependencies
- Add BETA_DEPLOYMENT.md with setup instructions
- Add README.md documenting beta features
- Update project structure for beta testing"

# Push beta branch
git push origin beta
```

### 4. Set Up Branch Protection (Optional)

On GitHub, you can set up branch protection for the beta branch:
- Go to repository Settings > Branches
- Add rule for `beta` branch
- Enable required reviews for pull requests
- Restrict direct pushes to beta branch

## 🔄 Syncing Workflow

### Daily Development

```bash
# Start work on beta branch
git checkout beta

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Beta feature: [description]"

# Push to beta
git push origin beta
```

### Sync with Main Repository

```bash
# Fetch latest from main
git fetch upstream

# Merge main into beta
git checkout beta
git merge upstream/master

# Resolve conflicts if any
# Test thoroughly

# Push updated beta
git push origin beta
```

### Create Pull Request

When ready to merge beta features back to main:
1. Go to main repository
2. Create pull request from `xomnia/project_tracker_beta:beta` to `xomnia/project_tracker:master`
3. Review and merge

## 📁 Beta File Structure

Your beta repository now includes:

```
project_tracker/
├── app.py                    # Main application (unchanged)
├── wsgi.py                   # WSGI entry point
├── requirements.txt          # Core dependencies
├── requirements-beta.txt     # Beta-specific dependencies
├── beta_config.py           # Beta configuration
├── README.md                # Beta documentation
├── BETA_DEPLOYMENT.md       # Beta deployment guide
├── DEPLOYMENT.md            # Original deployment guide
├── .gitignore               # Git ignore rules
└── templates/               # HTML templates
    ├── base.html
    ├── index.html
    ├── project_detail.html
    ├── add_project.html
    ├── edit_project.html
    └── partials/
        ├── _variant_list.html
        └── decision_modal.html
```

## 🚀 Next Steps

1. **Set up the beta branch** using the git commands above
2. **Install beta dependencies**: `pip install -r requirements-beta.txt`
3. **Test the beta features** following BETA_DEPLOYMENT.md
4. **Customize beta_config.py** for your specific needs
5. **Start developing new features** on the beta branch

## 🔍 Troubleshooting

### Git Issues
- If git commands fail, try restarting your terminal
- Ensure you have git installed and in your PATH
- Check that you're in the correct directory

### Python Issues
- Use virtual environment: `python -m venv venv`
- Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)
- Install dependencies: `pip install -r requirements-beta.txt`

### Database Issues
- Beta version uses separate database: `tracker_beta.db`
- Initialize with: `python -c "from app import db; db.create_all()"`

---

**Note**: This setup creates a proper beta fork that you can develop independently while keeping it synced with your main repository.
