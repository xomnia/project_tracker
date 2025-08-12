"""
Beta Configuration for Project Tracker
This file contains beta-specific configurations and feature flags.
"""

# Beta Version Information
BETA_VERSION = "0.2.0-beta"
BETA_FEATURES_ENABLED = True

# Beta Feature Flags
ENABLE_EXPERIMENTAL_FEATURES = True
ENABLE_BETA_UI = True
ENABLE_DEBUG_MODE = True

# Beta Database Configuration
BETA_DB_NAME = "tracker_beta.db"
BETA_LOG_LEVEL = "DEBUG"

# Beta UI Customizations
BETA_THEME = "modern"
BETA_COLOR_SCHEME = "blue"

# Beta API Endpoints
BETA_API_VERSION = "v2"
ENABLE_BETA_API = True

# Beta Testing Configuration
ENABLE_BETA_LOGGING = True
BETA_LOG_FILE = "beta.log"
ENABLE_PERFORMANCE_MONITORING = True

# Beta Security Settings
BETA_SECRET_KEY = "beta_secret_key_change_in_production"
ENABLE_BETA_AUTH = False

def get_beta_config():
    """Get all beta configuration settings"""
    return {
        'version': BETA_VERSION,
        'features_enabled': BETA_FEATURES_ENABLED,
        'experimental_features': ENABLE_EXPERIMENTAL_FEATURES,
        'beta_ui': ENABLE_BETA_UI,
        'debug_mode': ENABLE_DEBUG_MODE,
        'db_name': BETA_DB_NAME,
        'log_level': BETA_LOG_LEVEL,
        'theme': BETA_THEME,
        'color_scheme': BETA_COLOR_SCHEME,
        'api_version': BETA_API_VERSION,
        'beta_api': ENABLE_BETA_API,
        'beta_logging': ENABLE_BETA_LOGGING,
        'log_file': BETA_LOG_FILE,
        'performance_monitoring': ENABLE_PERFORMANCE_MONITORING,
        'secret_key': BETA_SECRET_KEY,
        'beta_auth': ENABLE_BETA_AUTH
    }

def is_beta_feature_enabled(feature_name):
    """Check if a specific beta feature is enabled"""
    beta_config = get_beta_config()
    return beta_config.get(feature_name, False)
