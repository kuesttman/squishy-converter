"""Media transcoding functionality."""

import os
import uuid
import threading
import logging
import datetime
import shutil
import signal
from typing import Optional, List

from squishy.config import load_config
from squishy.database import db
from squishy.models import TranscodeJob, MediaItem
from squishy.effeffmpeg.effeffmpeg import (
    transcode as effeff_transcode,
    get_file_info,
    detect_capabilities,
)

# Configure logging
logger = logging.getLogger(__name__)


def detect_hw_accel(ffmpeg_path: str = "ffmpeg") -> dict:
    """Detect available hardware acceleration methods.
    
    This is a wrapper around effeffmpeg's detect_capabilities for compatibility.
    """
    try:
        capabilities = detect_capabilities(ffmpeg_path=ffmpeg_path, quiet=True)
        
        # Build a response compatible with what admin.py expects
        result = {
            "available": [],
            "recommended": {
                "method": None,
                "device": None
            }
        }
        
        # Check for NVIDIA NVENC
        if capabilities.get("nvenc", {}).get("available"):
            result["available"].append("nvenc")
            if not result["recommended"]["method"]:
                result["recommended"]["method"] = "nvenc"
                result["recommended"]["device"] = None
        
        # Check for Intel QSV
        if capabilities.get("qsv", {}).get("available"):
            result["available"].append("qsv")
            if not result["recommended"]["method"]:
                result["recommended"]["method"] = "qsv"
                result["recommended"]["device"] = "/dev/dri/renderD128"
        
        # Check for VAAPI
        if capabilities.get("vaapi", {}).get("available"):
            result["available"].append("vaapi")
            if not result["recommended"]["method"]:
                result["recommended"]["method"] = "vaapi"
                result["recommended"]["device"] = "/dev/dri/renderD128"
        
        # Always add software as fallback
        result["available"].append("software")
        if not result["recommended"]["method"]:
            result["recommended"]["method"] = "software"
        
        return result
        
    except Exception as e:
        logger.error(f"Error detecting hardware acceleration: {e}")
        return {
            "available": ["software"],
            "recommended": {
                "method": "software",
                "device": None
            }
        }

# Track running processes for cancellation
RUNNING_PROCESSES = {}
RUNNING_PROCESSES_LOCK = threading.Lock()


def apply_output_path_mapping(path: str) -> str:
    """Apply path mappings for Docker environment."""
    config = load_config()
    if hasattr(config, 'path_mappings') and config.path_mappings:
        for source, target in config.path_mappings.items():
            if path.startswith(source):
                return path.replace(source, target, 1)
    return path


def create_job(media_item: MediaItem, preset_name: str) -> TranscodeJob:
    """Create a new transcoding job."""
    # Ensure media_item is attached to session or exists in DB
    existing_media = MediaItem.query.get(media_item.id)
    if not existing_media:
        db.session.add(media_item)
    
    job_id = str(uuid.uuid4())
    job = TranscodeJob(
        id=job_id,
        media_id=media_item.id,
        preset_name=preset_name,
        status="pending",
    )
    
    db.session.add(job)
    db.session.commit()
    logger.debug(f"Created job with id={job_id}")
    return job


def get_job(job_id: str) -> Optional[TranscodeJob]:
    """Get a job by ID."""
    return TranscodeJob.query.get(job_id)


def get_all_jobs() -> List[TranscodeJob]:
    """Get all jobs ordered by creation date."""
    return TranscodeJob.query.order_by(TranscodeJob.created_at.desc()).all()


def get_running_job_count() -> int:
    """Get count of currently running jobs."""
    return TranscodeJob.query.filter_by(status="processing").count()


def get_pending_jobs() -> List[TranscodeJob]:
    """Get all pending jobs ordered by creation date."""
    return TranscodeJob.query.filter_by(status="pending").order_by(TranscodeJob.created_at.asc()).all()


def start_transcode(job: TranscodeJob, media_item: MediaItem, preset_name: str, output_dir: str):
    """Start or queue a transcoding job."""
    logger.debug(f"Starting transcode job={job.id} for media={media_item.id}, preset={preset_name}")
    
    config = load_config()
    max_jobs = config.max_concurrent_jobs
    current_running = get_running_job_count()
    
    if current_running < max_jobs:
        # Start immediately
        _start_transcode_job_thread(job.id, output_dir)
    else:
        logger.debug(f"Job {job.id} queued - max concurrent jobs reached")
        # Job stays pending, will be picked up by process_job_queue


def cancel_job(job_id: str) -> bool:
    """Cancel a transcoding job."""
    job = get_job(job_id)
    if not job:
        return False
    
    if job.status == "processing":
        # Try to kill the process
        with RUNNING_PROCESSES_LOCK:
            if job_id in RUNNING_PROCESSES:
                try:
                    proc = RUNNING_PROCESSES[job_id]
                    if hasattr(proc, 'terminate'):
                        proc.terminate()
                    elif hasattr(proc, 'kill'):
                        proc.kill()
                    del RUNNING_PROCESSES[job_id]
                except Exception as e:
                    logger.error(f"Error terminating process for job {job_id}: {e}")
        
        job.status = "cancelled"
        job.completed_at = datetime.datetime.utcnow()
        db.session.commit()
        return True
    
    elif job.status == "pending":
        job.status = "cancelled"
        job.completed_at = datetime.datetime.utcnow()
        db.session.commit()
        return True
    
    return False


def remove_job(job_id: str) -> bool:
    """Remove a completed, failed, or cancelled job from the database."""
    job = get_job(job_id)
    if not job:
        return False
    
    # Only allow removal of non-active jobs
    if job.status in ("completed", "failed", "cancelled"):
        db.session.delete(job)
        db.session.commit()
        return True
    
    return False


def process_job_queue():
    """Process the job queue based on the concurrency limit."""
    try:
        config = load_config()
        max_jobs = config.max_concurrent_jobs

        current_running = get_running_job_count()
        available_slots = max(0, max_jobs - current_running)

        if available_slots <= 0:
            return

        pending_jobs = get_pending_jobs()
        jobs_to_start = pending_jobs[:available_slots]
        
        for job in jobs_to_start:
            output_dir = config.transcode_path 
            _start_transcode_job_thread(job.id, output_dir)
            
    except Exception as e:
        logger.error(f"Error processing job queue: {e}")


def _run_job_logic(app, job_id, output_dir):
    """Actual transcoding logic running in a thread."""
    with app.app_context():
        # Re-fetch objects in this thread's session
        job = TranscodeJob.query.get(job_id)
        if not job or not job.media:
            return

        media_item = job.media
        preset_name = job.preset_name
        config = load_config()
        
        try:
            # Update Status
            job.status = "processing"
            job.started_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Determine Output Path
            filename = os.path.basename(media_item.path)
            name, ext = os.path.splitext(filename)
            
            # Preset info
            preset = config.presets.get(preset_name, {})
            container = preset.get('container', '.mp4')
            
            output_filename = f"{name}-{preset_name}{container}"
            output_path = os.path.join(output_dir, output_filename)
            
            job.output_path = output_path
            
            # Get duration from media info
            try:
                file_info = get_file_info(media_item.path, config.ffprobe_path)
                if file_info and 'format' in file_info:
                    job.duration = float(file_info['format'].get('duration', 0))
            except Exception as e:
                logger.warning(f"Could not get duration for {media_item.path}: {e}")
            
            db.session.commit()

            # Progress Callback
            def progress_callback(line, progress):
                try:
                    if progress is not None:
                        job.progress = min(progress, 0.99)
                        db.session.commit()
                except Exception as ex:
                    logger.error(f"Progress update error: {ex}")

            # Run Transcode with correct parameters
            result = effeff_transcode(
                input_file=media_item.path,
                output_file=output_path,
                presets_data={preset_name: preset},
                preset_name=preset_name,
                progress_callback=progress_callback,
                overwrite=True,
                quiet=True
            )
            
            # Completion
            job.status = "completed"
            job.progress = 1.0
            job.completed_at = datetime.datetime.utcnow()
            
            # Get final size
            if os.path.exists(output_path):
                job.output_size = str(os.path.getsize(output_path))

            db.session.commit()
            
            # Trigger next job
            process_job_queue()

        except Exception as e:
            logger.error(f"Transcode failed for job {job_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Still try to process next jobs
            process_job_queue()


def _start_transcode_job_thread(job_id, output_dir):
    """Start the transcoding thread."""
    from flask import current_app
    app = current_app._get_current_object()
    
    t = threading.Thread(target=_run_job_logic, args=(app, job_id, output_dir))
    t.daemon = True
    t.start()

