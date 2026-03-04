"""
File based artifact store with TTL cleanup.
Stores execution output artifacts (PNG, HTML, CSV) with UUID keys
and automatically cleans up expired artifacts
"""

import datetime
import json
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class ArtifactInfo:
    """Metadata about a stored artifact"""

    artifact_id: str
    filename: str
    content_type: str
    size_bytes: int


# Map file extensions to MIME types
_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".html": "text/html",
    ".csv": "text/csv",
    ".json": "application/json",
    ".txt": "text/plain",
}


class ArtifactStore:
    """File-based artifact store with TTL cleanup."""

    def __init__(
        self,
        base_dir: str = "/tmp/epi-geo-artifacts",
        ttl_minutes: int = 60,
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = datetime.timedelta(minutes=ttl_minutes)

    def store(self, source_path: Path) -> ArtifactInfo:
        """
        Store an artifact file and return its metadata.
        Args:
            source_path: Path to the file to store.
        Returns:
            ArtifactInfo with the assigned artifact_id, filename, content_type, and size.
        """
        artifact_id = str(uuid.uuid4())
        suffix = source_path.suffix.lower()
        content_type = _CONTENT_TYPES.get(suffix, "application/octet-stream")

        # copy file to store
        dest = self.base_dir / f"{artifact_id}{suffix}"
        shutil.copy2(source_path, dest)

        # write metadata
        meta = {
            "content_type": content_type,
            "filename": source_path.name,
            "suffix": suffix,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        (self.base_dir / f"{artifact_id}.meta").write_text(json.dumps(meta))

        return ArtifactInfo(
            artifact_id=artifact_id,
            filename=source_path.name,
            content_type=content_type,
            size_bytes=dest.stat().st_size,
        )

    def get(self, artifact_id: str) -> Optional[Tuple[Path, str, str]]:
        """
        Retrieve an artifact by ID.
        Returns:
            Tuple of (file_path, content_type, original_filename_ or None if not found/expired.
        """
        meta_path = self.base_dir / f"{artifact_id}.meta"

        if not meta_path.exists():
            return None

        meta = json.loads(meta_path.read_text())
        suffix = meta.get("suffix", "")
        artifact_path = self.base_dir / f"{artifact_id}{suffix}"

        if not artifact_path.exists():
            return None

        created_at = datetime.datetime.fromisoformat(meta["created_at"])

        # check TTL
        if datetime.datetime.now(datetime.UTC) - created_at > self.ttl:
            self._remove(artifact_id)
            return None

        return artifact_path, meta["content_type"], meta["filename"]

    def cleanup_expired(self) -> int:
        """Remove all expired artifacts, Returns count of removed artifacts."""
        removed = 0
        for meta_path in self.base_dir.glob("*.meta"):
            artifact_id = meta_path.stem
            try:
                meta = json.loads(meta_path.read_text())
                created_at = datetime.datetime.fromisoformat(meta["created_at"])
                if datetime.datetime.now(datetime.UTC) - created_at > self.ttl:
                    self._remove(artifact_id)
                    removed += 1
            except (json.JSONDecodeError, KeyError):
                self._remove(artifact_id)
                removed += 1
        return removed

    def _remove(self, artifact_id: str) -> None:
        """Remove an artifact and its metadata file based on the artifact id."""
        meta_path = self.base_dir / f"{artifact_id}.meta"
        # Read suffix from metadata to find the actual artifact file
        suffix = ""
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                suffix = meta.get("suffix", "")
            except (json.JSONDecodeError, KeyError):
                pass
        artifact_path = self.base_dir / f"{artifact_id}{suffix}"
        artifact_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
