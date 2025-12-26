"""Automation Scheduler for Squishy."""

import threading
import time
import logging
from flask import Flask
from squishy.config import load_config
from squishy.scanner import scan_jellyfin, scan_plex, get_all_media, get_scan_status
from squishy.transcoder import create_job, calculate_output_path
from squishy.models import TranscodeJob

# Global scheduler thread reference
_scheduler_thread = None
_stop_event = threading.Event()
_scheduler_lock = threading.Lock()

def start_scheduler(app: Flask):
    """Start the automation scheduler in a background thread."""
    global _scheduler_thread
    with _scheduler_lock:
        if _scheduler_thread is None or not _scheduler_thread.is_alive():
            _stop_event.clear()
            _scheduler_thread = threading.Thread(
                target=_scheduler_loop, 
                args=(app,), 
                daemon=True,
                name="SquishyScheduler"
            )
            _scheduler_thread.start()
            app.logger.info("Automation Scheduler started")

def stop_scheduler():
    """Stop the automation scheduler."""
    global _scheduler_thread
    if _scheduler_thread:
        _stop_event.set()
        _scheduler_thread.join(timeout=2)
        _scheduler_thread = None
        logging.info("Automation Scheduler stopped")

def _run_auto_squish(app: Flask):
    """Check for new media and queue transcode jobs."""
    with app.app_context():
        config = load_config()
        if not config.auto_squish_enabled:
            return

        app.logger.debug("Auto-Squish: Checking for untranscoded media...")
        
        # Get all media currently known
        all_media = get_all_media()
        
        # Get all existing jobs (media_id, output_path)
        # We fetch all jobs to check against specific output paths
        existing_jobs = TranscodeJob.query.with_entities(TranscodeJob.media_id, TranscodeJob.output_path).all()
        existing_job_map = set() # Set of (media_id, output_path)
        existing_media_ids_simple = set() # Fallback for simple mode
        
        for mid, out_path in existing_jobs:
            if out_path:
                existing_job_map.add((mid, out_path))
            existing_media_ids_simple.add(mid)

        items_queued = 0

        # Determine versions to create
        versions = config.versions or []
        # Fallback to single preset if no versions defined but auto_squish_preset is set
        if notVersions := (not versions and config.auto_squish_preset):
             pass # Logic handled inside loop
        
        for item in all_media:
            jobs_to_create = []
            
            if versions:
                # Multi-version mode
                for version in versions:
                    preset_name = version.get("preset")
                    suffix = version.get("suffix")
                    
                    if not preset_name: 
                        continue
                        
                    # Calculate expected path
                    try:
                        expected_path = calculate_output_path(item, preset_name, suffix)
                        
                        # Check if duplicate
                        if (item.id, expected_path) in existing_job_map:
                            continue
                            
                        jobs_to_create.append((preset_name, suffix))
                    except Exception as ex:
                        app.logger.error(f"Error calculating path for {item.title}: {ex}")
            
            elif config.auto_squish_preset:
                # Simple mode (Backwards compatibility)
                if item.id in existing_media_ids_simple:
                    continue
                jobs_to_create.append((config.auto_squish_preset, None))

            # Create the jobs
            for preset_name, suffix in jobs_to_create:
                try:
                    app.logger.info(f"Auto-Squish: Queuing job for {item.title} ({preset_name})")
                    create_job(item, preset_name, suffix)
                    items_queued += 1
                except Exception as e:
                    app.logger.error(f"Failed to auto-squish {item.title}: {e}")

        if items_queued > 0:
            app.logger.info(f"Auto-Squish: Queued {items_queued} new jobs.")
            # Trigger queue processing to start jobs if slots available
            from squishy.transcoder import process_job_queue
            process_job_queue()
        else:
             app.logger.debug("Auto-Squish: No new media to transcode.")

def _scheduler_loop(app: Flask):
    """Main scheduler loop running in background thread."""
    last_scan_time = 0
    
    # Initial delay to let app startup completely
    time.sleep(10)
    
    with app.app_context():
        app.logger.info("Scheduler loop initialized")

    while not _stop_event.is_set():
        try:
            # Re-create app context for each iteration to ensure fresh DB session
            with app.app_context():
                config = load_config()
                
                # Check Auto-Scan Interval
                # Check if scan is already running first
                scan_status = get_scan_status()
                if scan_status.get("in_progress"):
                    pass # Scan in progress, wait
                elif config.auto_scan_interval > 0:
                    now = time.time()
                    interval_seconds = config.auto_scan_interval * 60
                    
                    # If enough time passed since last scan
                    if (now - last_scan_time) > interval_seconds:
                        app.logger.info(f"Auto-Scan triggered (Interval: {config.auto_scan_interval}m)")
                        
                        # Run Synchronous Scan
                        items_found = 0
                        
                        # Use internal scanner functions directly to block
                        if config.jellyfin_url and config.jellyfin_api_key:
                            app.logger.info("Auto-Scan: Starting Jellyfin Scan...")
                            items = scan_jellyfin(config.jellyfin_url, config.jellyfin_api_key)
                            items_found = len(items)
                        elif config.plex_url and config.plex_token:
                            app.logger.info("Auto-Scan: Starting Plex Scan...")
                            items = scan_plex(config.plex_url, config.plex_token)
                            items_found = len(items)
                        
                        last_scan_time = time.time()
                        app.logger.info(f"Auto-Scan completed. Found {items_found} items.")
                        
                        # Trigger Auto-Squish after successful scan
                        if config.auto_squish_enabled:
                            _run_auto_squish(app)
                            
        except Exception as e:
            logging.error(f"Scheduler loop error: {e}")
        
        # Sleep loop (check stop event frequently)
        for _ in range(60): # Sleep 60s total
            if _stop_event.is_set():
                break
            time.sleep(1)
