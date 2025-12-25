"""
Library Manager for Squishy.
Handles local file scanning, metadata extraction, and report generation.
"""

import os
import logging
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

from squishy.config import load_config
from squishy.effeffmpeg.effeffmpeg import get_file_info

# Configure logging
logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {
    '.mkv', '.mp4', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v', '.ts', '.m2ts'
}

class LibraryManager:
    """Manages local media library scanning and reporting."""

    def __init__(self):
        self.config = load_config()
        
    def scan_path(self, path: Optional[str] = None, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scan a directory for video files and extract metadata.
        
        Args:
            path: Directory path to scan. If None, uses config.media_path.
            recursive: Whether to scan recursively.
            
        Returns:
            List of dictionaries containing media metadata.
        """
        scan_root = path if path else self.config.media_path
        if not os.path.exists(scan_root):
            logger.error(f"Scan path does not exist: {scan_root}")
            return []
            
        logger.info(f"Starting deep scan of {scan_root} (recursive={recursive})")
        media_files = []
        
        try:
            if recursive:
                for root, _, files in os.walk(scan_root):
                    for file in files:
                        if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                            full_path = os.path.join(root, file)
                            media_files.append(full_path)
            else:
                 for item in os.listdir(scan_root):
                    full_path = os.path.join(scan_root, item)
                    if os.path.isfile(full_path) and os.path.splitext(item)[1].lower() in VIDEO_EXTENSIONS:
                        media_files.append(full_path)
                        
            logger.info(f"Found {len(media_files)} video files. Extracting metadata...")
            
            results = []
            for file_path in media_files:
                try:
                    info = self._analyze_file(file_path)
                    if info:
                        results.append(info)
                except Exception as e:
                    logger.warning(f"Failed to analyze file {file_path}: {e}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error during library scan: {e}")
            return []

    def _analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract detailed metadata for a single file using ffprobe."""
        # Basic file info
        stat = os.stat(file_path)
        file_size = stat.st_size
        created_time = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        
        # FFprobe info
        probe_info = get_file_info(file_path, self.config.ffprobe_path)
        if not probe_info:
            logger.warning(f"Could not probe file: {file_path}")
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": file_size,
                "created": created_time,
                "error": "Probe failed"
            }
            
        # Parse relevant streams
        video_streams = [s for s in probe_info.get("streams", []) if s["codec_type"] == "video"]
        audio_streams = [s for s in probe_info.get("streams", []) if s["codec_type"] == "audio"]
        subtitle_streams = [s for s in probe_info.get("streams", []) if s["codec_type"] == "subtitle"]
        
        main_video = video_streams[0] if video_streams else {}
        
        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "container": os.path.splitext(file_path)[1].lower(),
            "size": file_size,
            "duration": float(probe_info.get("format", {}).get("duration", 0)),
            "bitrate": probe_info.get("format", {}).get("bit_rate"),
            "video_codec": main_video.get("codec_name"),
            "video_profile": main_video.get("profile"),
            "width": main_video.get("width"),
            "height": main_video.get("height"),
            "audio_codecs": [a.get("codec_name") for a in audio_streams],
            "audio_channels": [a.get("channels") for a in audio_streams],
            "subtitle_codecs": [s.get("codec_name") for s in subtitle_streams],
            "subtitle_langs": [s.get("tags", {}).get("language") for s in subtitle_streams],
            "created": created_time
        }

    def generate_report(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistical report from scanned items."""
        total_items = len(items)
        if total_items == 0:
             return {"total_items": 0, "generated_at": datetime.datetime.now().isoformat()}

        total_size = sum(item.get("size", 0) for item in items)
        total_duration = sum(item.get("duration", 0) for item in items)
        
        # Distributions
        containers = Counter(item.get("container") for item in items)
        video_codecs = Counter(item.get("video_codec") for item in items)
        resolutions = Counter(f"{item.get('width')}x{item.get('height')}" for item in items if item.get("width"))
        
        audio_count = 0
        subtitle_count = 0
        for item in items:
            audio_count += len(item.get("audio_codecs", []))
            subtitle_count += len(item.get("subtitle_codecs", []))
            
        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "scan_summary": {
                "total_files": total_items,
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size / (1024**3), 2),
                "total_duration_hours": round(total_duration / 3600, 2)
            },
            "distributions": {
                "containers": dict(containers),
                "video_codecs": dict(video_codecs),
                "resolutions": dict(resolutions)
            },
            "stream_stats": {
                "total_audio_streams": audio_count,
                "total_subtitle_streams": subtitle_count,
                "avg_audio_per_file": round(audio_count / total_items, 1),
                "avg_subs_per_file": round(subtitle_count / total_items, 1)
            }
        }
