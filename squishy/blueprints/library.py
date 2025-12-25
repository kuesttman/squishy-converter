from flask import Blueprint, jsonify, request, render_template
import threading
import logging
import uuid
import os
import datetime
from flask_login import login_required
from squishy.library_manager import LibraryManager
from squishy.transcoder import create_job, process_job_queue
from squishy.models import Movie
from squishy.config import load_config
from squishy.database import db

library_bp = Blueprint('library', __name__, url_prefix='/library')
logger = logging.getLogger(__name__)

# Shared state for scanning
SCAN_LOCK = threading.Lock()
SCAN_STATE = {
    "is_scanning": False,
    "started_at": None,
    "items_processed": 0,
    "total_items_estimated": 0, # Not easy to estimate deeply
    "last_report": None,
    "items": [], # Store list of scanned items
    "error": None
}

def run_scan_thread(recursive=True):
    """Background thread function for scanning."""
    global SCAN_STATE
    manager = LibraryManager()
    
    try:
        items = manager.scan_path(recursive=recursive)
        report = manager.generate_report(items)
        
        with SCAN_LOCK:
            SCAN_STATE["is_scanning"] = False
            SCAN_STATE["last_report"] = report
            SCAN_STATE["items"] = items
            SCAN_STATE["items_processed"] = len(items)
            
        logger.info("Library scan completed successfully.")
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        with SCAN_LOCK:
            SCAN_STATE["is_scanning"] = False
            SCAN_STATE["error"] = str(e)

@library_bp.route('/batch_queue', methods=['POST'])
@login_required
def batch_queue():
    """Queue multiple files for transcoding."""
    data = request.json
    if not data or 'files' not in data:
        return jsonify({"status": "error", "message": "No files provided"}), 400
        
    files = data['files'] # List of paths
    preset_name = data.get('preset', 'high')
    
    config = load_config()
    if preset_name not in config.presets:
         return jsonify({"status": "error", "message": f"Preset '{preset_name}' not found"}), 400
         
    queued_count = 0
    
    try:
        for file_path in files:
            if not os.path.exists(file_path):
                logger.warning(f"File not found for batch queue: {file_path}")
                continue
                
            media_id = str(uuid.uuid4())
            filename = os.path.basename(file_path)
            title, _ = os.path.splitext(filename)
            
            movie = Movie(
                id=media_id,
                title=title,
                path=file_path,
                overview="Imported from Deep Scan"
            )
            
            # Create Job - create_job handles DB session addition
            create_job(movie, preset_name)
            queued_count += 1
            
        # Trigger processing
        process_job_queue()
        
        return jsonify({
            "status": "success", 
            "message": f"Queued {queued_count} files successfully.",
            "count": queued_count
        })
        
    except Exception as e:
        logger.error(f"Error in batch queue: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@library_bp.route('/')
@login_required
def index():
    """Library Dashboard."""
    return render_template('library_report.html', report=SCAN_STATE["last_report"], scanning=SCAN_STATE["is_scanning"])

@library_bp.route('/scan', methods=['POST'])
@login_required
def start_scan():
    """Trigger a new library scan."""
    global SCAN_STATE
    
    with SCAN_LOCK:
        if SCAN_STATE["is_scanning"]:
            return jsonify({"status": "error", "message": "Scan already in progress"}), 409
            
        SCAN_STATE["is_scanning"] = True
        SCAN_STATE["started_at"] = datetime.datetime.now().isoformat()
        SCAN_STATE["error"] = None
        SCAN_STATE["items_processed"] = 0
        
    # Start thread
    thread = threading.Thread(target=run_scan_thread, kwargs={'recursive': True})
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "message": "Scan started"})

@library_bp.route('/status')
@login_required
def status():
    """Get current scan status."""
    return jsonify(SCAN_STATE)

@library_bp.route('/report')
@login_required
def get_report():
    """Get JSON report."""
    if not SCAN_STATE["last_report"]:
         return jsonify({"status": "empty", "message": "No report generated yet."}), 404
    return jsonify(SCAN_STATE["last_report"])

@library_bp.route('/items')
@login_required
def get_items():
    """Get scanned items list."""
    if not SCAN_STATE["items"]:
         return jsonify({"items": []})
    return jsonify({"items": SCAN_STATE["items"]})
