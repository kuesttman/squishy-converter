"""Main Squishy application."""

import os
import logging
from flask import Flask, redirect, url_for, request, session
from flask_socketio import SocketIO

from squishy.config import load_config, Config, is_first_run
from squishy.blueprints.api import api_bp
from squishy.blueprints.ui import ui_bp
from squishy.blueprints.admin import admin_bp
from squishy.blueprints.onboarding import onboarding_bp
from squishy import scanner

# Initialize SocketIO globally
socketio = SocketIO()

def perform_initial_scan(config: Config):
    """Perform initial scan of media if Jellyfin or Plex is configured."""
    if config.jellyfin_url and config.jellyfin_api_key:
        logging.debug("Jellyfin configuration found. Starting initial scan in background...")
        scanner.scan_jellyfin_async(config.jellyfin_url, config.jellyfin_api_key)
    elif config.plex_url and config.plex_token:
        logging.debug("Plex configuration found. Starting initial scan in background...")
        scanner.scan_plex_async(config.plex_url, config.plex_token)
    else:
        logging.warning("No media server configuration found. Please configure Jellyfin or Plex to use Squishy.")

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration from config file
    config = load_config()

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", config.secret_key or "squishy_dev_secret_key"),
        MEDIA_PATH=config.media_path,
        TRANSCODE_PATH=config.transcode_path,
    )
    
    # Disable template caching in development mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Load test configuration if provided
    if test_config is not None:
        app.config.from_mapping(test_config)

    # Ensure the transcode folder exists
    try:
        os.makedirs(app.config["TRANSCODE_PATH"], exist_ok=True)
    except OSError:
        pass

    # Register blueprints
    from squishy.blueprints.auth import auth_bp
    from squishy.blueprints.library import library_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ui_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(onboarding_bp, url_prefix="/onboarding")
    app.register_blueprint(library_bp)
    
    # Initialize SocketIO with the app
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
    
    
    # Initialize Extensions
    # Use /config directory for the database (mounted volume in Docker)
    db_dir = os.environ.get('CONFIG_PATH', '/config')
    if not db_dir.endswith('/'):
        db_dir_base = os.path.dirname(db_dir) if db_dir.endswith('.json') else db_dir
    else:
        db_dir_base = db_dir
    
    # Ensure directory exists
    os.makedirs(db_dir_base, exist_ok=True)
    
    db_path = os.path.join(db_dir_base, 'squishy.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from squishy.database import init_db
    init_db(app)

    # Initialize LoginManager
    from flask_login import LoginManager
    from squishy.user import User
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Initialize Flask-Babel
    from flask_babel import Babel
    
    def get_locale():
        if 'language' in session:
            return session['language']
        # Try to get from config
        try:
            config = load_config()
            return config.language
        except:
            pass
        return request.accept_languages.best_match(['pt_BR', 'en'])

    babel = Babel(app, locale_selector=get_locale)

    # Add a before_request handler to check if this is the first run
    @app.before_request
    def check_first_run():
        # Skip for onboarding and static routes
        if request.path.startswith('/static') or request.path.startswith('/onboarding') or request.path.startswith('/login') or request.path.startswith('/set_language'):
            return None
            
        # Skip for API routes as well (protect them separately if needed, or rely on token/same auth)
        # Note: Depending on API usage, might need Basic Auth or ensuring session cookie is sent.
        if request.path.startswith('/api'):
            return None
            
        # If socket.io connections, allow them
        if request.path.startswith('/socket.io'):
            return None
            
        # If it's the first run or we're in an onboarding process and not already on the onboarding page, redirect
        first_run = is_first_run()
        onboarding_active = 'onboarding_in_progress' in session and session.get('onboarding_in_progress')
        
        # Clear onboarding flag if first_run is false but session still has the flag
        if not first_run and onboarding_active:
            # Check if we have a valid media server configuration
            config = load_config()
            has_jellyfin = config.jellyfin_url and config.jellyfin_api_key
            has_plex = config.plex_url and config.plex_token
            
            # If we have a valid configuration but still have the flag,
            # clear it (configuration must have been saved manually)
            if has_jellyfin or has_plex:
                session.pop('onboarding_in_progress', None)
                session.modified = True
                onboarding_active = False
        
        # Redirect to onboarding if needed
        if (first_run or onboarding_active) and not request.path.startswith('/onboarding'):
            return redirect(url_for('onboarding.index'))
            
        return None

    # Perform initial scan if media server is configured and not in first run
    if not test_config and not is_first_run():  # Skip scan during testing or first run
        perform_initial_scan(config)
        
        # Start Automation Scheduler
        from squishy.scheduler import start_scheduler
        start_scheduler(app)

    return app

def main():
    """Run the application."""
    # Logging is configured in run.py, but update here in case app.py is run directly
    config = load_config()
    log_level = os.environ.get('LOG_LEVEL', config.log_level).upper()
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Create Flask app
    app = create_app()

    # Run with SocketIO instead of Flask's built-in server
    socketio.run(app, host="0.0.0.0", port=5101, debug=os.environ.get("DEBUG", "False").lower() == "true")

if __name__ == "__main__":
    main()
