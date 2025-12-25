#!/usr/bin/env python3
"""Entry point for the Squishy application."""

import os
import logging
import eventlet

# Patch stdlib for eventlet/WebSocket support
eventlet.monkey_patch()

from squishy.app import main  # noqa

if __name__ == "__main__":
    # Load config to get log level
    from squishy.config import load_config

    config = load_config()

    # Configure logging with level from config, overridden by environment variable if set
    log_level = os.environ.get("LOG_LEVEL", config.log_level).upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Log startup information
    logging.info(f"🚀 Squishy starting with log level: {log_level}")
    logging.info(f"📁 Media path: {config.media_path}")
    logging.info(f"🔒 Auth enabled: {config.auth_enabled}")

    # Start the app
    main()
