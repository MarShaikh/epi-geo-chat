"""
Docker sandbox for executing generated Python code securely.

Runs code in an isolated container with resource limits,
and read-only filesystem (except /workspace/output/).
Network access is allowed so rasterio/GDAL can fetch COGs via signed URLs.
"""

import asyncio
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import docker
from docker.errors import APIError, ContainerError, ImageNotFound

from src.code_executor.artifact_store import ArtifactInfo, ArtifactStore

# When the backend runs inside Docker and spawns sandbox containers via the
# Docker socket, bind mount paths must be resolvable by the Docker daemon
# (i.e. on the host). SANDBOX_TEMP_DIR sets a shared directory that is
# mounted into both the backend container and visible to the host.
# See docs/local-development.md for details.
SANDBOX_TEMP_DIR = os.environ.get("SANDBOX_TEMP_DIR", None)


@dataclass
class ExecutionResult:
    """Result of sandboxed code execution."""

    success: bool
    stdout: str
    stderr: str
    artifacts: List[ArtifactInfo] = field(default_factory=list)
    execution_time_ms: int = 0
    error: Optional[str] = None


IMAGE_NAME = "epi-geo-sandbox:latest"
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_MEM_LIMIT = "512m"


class DockerSandbox:
    """Executes Python code in a docker container with security constraints"""

    def __init__(self, artifact_store: ArtifactStore):
        self.client = docker.from_env()
        self.artifact_store = artifact_store

    async def execute(
        self,
        code: str,
        input_data: dict,
        timeout_seconds: int = DEFAULT_TIMEOUT,
    ) -> ExecutionResult:
        """Execute code in a sandboxed Docker container.
        Args:
            code: Python code to execute
            input_data: Dict with user_query, bbox, datetime, collections, items (items include full signed asset URLs).
            timeout_seconds: Max Execution time before kill.

        Returns:
            ExecutionResult with stdout, stderr, artifacts, and timing.
        """
        # Run the blocking Docker operation in a thread
        return await asyncio.to_thread(
            self._execute_sync, code, input_data, timeout_seconds
        )

    def _execute_sync(
        self,
        code: str,
        input_data: dict,
        timeout_seconds: int,
    ) -> ExecutionResult:
        """Synchronous Docker execution (called via asyncio.to_thread)"""

        tmpdir = tempfile.mkdtemp(
            prefix="epi-sandbox-", dir=SANDBOX_TEMP_DIR
        )
        input_dir = Path(tmpdir) / "input"
        output_dir = Path(tmpdir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # write input files
        (input_dir / "data.json").write_text(json.dumps(input_data, default=str))
        (input_dir / "script.py").write_text(code)
        container = None
        start_time = time.monotonic()

        try:
            container = self.client.containers.run(
                IMAGE_NAME,
                command=["python", "/workspace/input/script.py"],
                volumes={
                    str(input_dir): {"bind": "/workspace/input", "mode": "ro"},
                    str(output_dir): {"bind": "/workspace/output", "mode": "rw"},
                },
                mem_limit=DEFAULT_MEM_LIMIT,
                nano_cpus=1_000_000_000,  # 1 CPU
                # network_mode="bridge" (default) — needed for rasterio/GDAL
                # to fetch COGs via signed URLs. AST validator blocks
                # http/urllib/socket/subprocess imports for security.
                read_only=True,
                tmpfs={"/tmp": "size=100m"},
                detach=True,
            )

            # Wait for completion with timeout
            result = container.wait(timeout=timeout_seconds)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)

            stdout = container.logs(stdout=True, stderr=False).decode(
                "utf-8", errors="replace"
            )
            stderr = container.logs(stdout=False, stderr=True).decode(
                "utf-8", errors="replace"
            )
            exit_code = result.get("StatusCode", -1)

            # collect artifacts from output directory
            artifacts = self._collect_artifacts(output_dir)

            return ExecutionResult(
                success=exit_code == 0,
                stdout=stdout[-5000:],  # Limit output size
                stderr=stderr[-2000:],
                artifacts=artifacts,
                execution_time_ms=elapsed_ms,
                error=stderr[-500:] if exit_code != 0 else None,
            )

        except (ContainerError, APIError) as e:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                execution_time_ms=elapsed_ms,
                error=f"Container_error: {e}",
            )
        except Exception as e:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            # timeout or other exceptions
            if container:
                try:
                    container.kill()
                except Exception:
                    pass
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                execution_time_ms=elapsed_ms,
                error=f"Execution failed: {e}",
            )
        finally:
            # cleanup container
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _collect_artifacts(self, output_dir: Path) -> List[ArtifactInfo]:
        """Scan output directory and store artifacts"""
        artifacts = []
        for path in output_dir.iterdir():
            if path.is_file() and path.stat().st_size > 0:
                info = self.artifact_store.store(path)
                artifacts.append(info)
        return artifacts
