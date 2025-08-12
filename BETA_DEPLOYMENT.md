# Beta Deployment Guide

This guide covers deploying and running the Project Tracker Beta version.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install beta dependencies
pip install -r requirements-beta.txt
```

### 2. Configuration

The beta version uses `beta_config.py` for configuration. Key settings:

- **Database**: Uses `tracker_beta.db` by default
- **Debug Mode**: Enabled by default for beta testing
- **Logging**: Enhanced logging to `beta.log`
- **Performance Monitoring**: Enabled for beta testing

### 3. Database Setup

```bash
# Initialize the database (first run only)
python -c "from app import db; db.create_all()"
```

### 4. Run Beta Version

```bash
# Development mode
python app.py

# Production mode (recommended for testing)
python wsgi.py
```

## 🔧 Beta-Specific Features

### Enhanced Logging
- All beta operations are logged to `beta.log`
- Performance metrics are captured
- Debug information is available

### Performance Monitoring
- Flask-Profiler integration
- Memory usage tracking
- Response time monitoring

### API Endpoints
- RESTful API available at `/api/v2/`
- Enhanced error handling
- Request/response logging

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask coverage

# Run tests
pytest

# Run with coverage
coverage run -m pytest
coverage report
```

### Manual Testing
1. Create a test project
2. Add tasks with dependencies
3. Test file uploads
4. Verify business day calculations
5. Check performance metrics

## 📊 Monitoring

### Log Files
- `beta.log` - Application logs
- `performance.log` - Performance metrics
- `error.log` - Error tracking

### Performance Metrics
- Response times
- Memory usage
- Database query performance
- User interaction patterns

## 🔄 Syncing with Main Repository

### Update from Main
```bash
# Add upstream remote
git remote add upstream https://github.com/xomnia/project_tracker.git

# Fetch latest changes
git fetch upstream

# Merge main branch
git merge upstream/master

# Resolve conflicts if any
# Test thoroughly after merge
```

### Push Beta Changes
```bash
# Commit beta changes
git add .
git commit -m "Beta feature: [description]"

# Push to beta repository
git push origin beta
```

## 🚨 Beta Considerations

### Stability
- This is a beta version - expect occasional issues
- Features may change without notice
- Database schema may evolve

### Backup
- Always backup your beta database before updates
- Test in development environment first
- Keep main repository as fallback

### Reporting Issues
- Use the beta repository's issue tracker
- Include logs and reproduction steps
- Tag issues with `beta` label

## 🔐 Security Notes

- Beta version uses development secret keys
- Authentication is disabled by default
- CORS is enabled for development
- Change default passwords and keys in production

## 📈 Performance Tips

- Monitor memory usage during extended testing
- Check database performance with large datasets
- Use Flask-Profiler to identify bottlenecks
- Enable caching for frequently accessed data

---

**Remember**: This is a beta version intended for testing and feedback. Not recommended for production use without thorough testing.
