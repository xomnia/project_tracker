# 🚀 PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere free account (https://www.pythonanywhere.com/)
- Your project files uploaded to PythonAnywhere

## Step-by-Step Deployment

### 1. Upload Your Files
1. Go to your PythonAnywhere dashboard
2. Click on "Files" tab
3. Create a new directory (e.g., `project_tracker`)
4. Upload all your project files to this directory:
   - `app.py`
   - `requirements.txt`
   - `wsgi.py`
   - `templates/` folder
   - Any other project files

### 2. Set Up Virtual Environment
**Yes, you need to create a virtual environment!** This is important to avoid dependency conflicts.

1. Go to "Consoles" tab
2. Start a new Bash console
3. Navigate to your project directory:
   ```bash
   cd project_tracker
   ```
4. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.9 project_tracker_env
   ```
5. Activate the environment:
   ```bash
   workon project_tracker_env
   ```
6. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

**Why you need this:**
- Isolates your app's dependencies from other apps
- Ensures you have the exact versions specified in requirements.txt
- Prevents conflicts with PythonAnywhere's system packages
- Required for proper deployment

### 3. Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration" (not Django)
4. Select Python version 3.9
5. Set your source code directory to `/home/yourusername/project_tracker`
6. Set your working directory to `/home/yourusername/project_tracker`
7. **Important**: Set your virtual environment path to `/home/yourusername/.virtualenvs/project_tracker_env`

### 4. Configure WSGI File
1. In the "Web" tab, click on the WSGI configuration file link
2. Replace the content with:
   ```python
   import sys
   import os
   
   # Add the project directory to the Python path
   path = '/home/yourusername/project_tracker'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app
   
   application = app
   ```
3. Replace `yourusername` with your actual PythonAnywhere username
4. Save the file

**Note**: The virtual environment path should be automatically detected if you set it correctly in step 3.

### 5. Set Environment Variables
1. In the "Web" tab, go to "Environment variables"
2. Add any environment variables if needed (none required for this app)

### 6. Reload Web App
1. Click the "Reload" button in the "Web" tab
2. Your app should now be accessible at `yourusername.pythonanywhere.com`

### 7. Test Your App
1. Visit your app URL
2. Test the main functionality:
   - Create a project
   - Add tasks
   - Add materials
   - Test variant selection/deselection

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure your virtual environment is activated and requirements are installed
2. **Database Issues**: The SQLite database will be created automatically in your project directory
3. **Static Files**: Make sure all template files are in the correct `templates/` directory
4. **Permission Issues**: Ensure all files have proper read permissions

### Debugging:
1. Check the error logs in the "Web" tab
2. Use the console to test imports manually
3. Verify file paths are correct for your username

## Security Notes
- The free tier has limitations on external network access
- SQLite database is stored in your project directory
- Debug mode should be disabled in production (set `debug=False` in app.py)

## Next Steps
- Consider upgrading to a paid plan for custom domains
- Set up automatic backups of your database
- Monitor your app's performance and logs
