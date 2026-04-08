"""
Visualization helper: ships a single structure file to the remote
`xrpa-ray-container` via the Ray Jobs API and launches VMD on the XPRA
display (:80).

The submitter runs OUTSIDE the container and talks to the Ray dashboard /
Jobs API on port 8265. The file is uploaded as part of the job's
`working_dir` (Ray zips it, sends it to the cluster, unpacks it in the
job's runtime env) — no shared mount or extra ports required.

`visualize()` blocks until the job finishes, which happens when the user
closes VMD. That's the per-step pause point.
"""

import logging
import shutil
import tempfile
import time
from pathlib import Path

from ray.job_submission import JobStatus, JobSubmissionClient

from research_work.config import (
    PAUSE_FOR_VISUALIZATION,
    RAY_JOBS_ADDRESS,
    XPRA_DISPLAY,
    VMD_COMMAND,
)


logger = logging.getLogger(__name__)


# This is the entrypoint that Ray runs INSIDE xrpa-ray-container.
# It is written to the job's working_dir alongside the structure file,
# so VMD can just open `./<filename>`. It blocks on VMD, so the job stays
# RUNNING until the user closes the window.
_ENTRYPOINT_TEMPLATE = """\
import logging, os, sys, subprocess

FILENAME = {filename!r}
DISPLAY  = {display!r}
VMD_CMD  = {vmd_cmd!r}

env = os.environ.copy()
env["DISPLAY"] = DISPLAY
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# VMD has its own C++ main loop that handles mouse input on the OpenGL
# window. If we block Tcl with `vwait forever`, that loop never runs and
# the molecule is frozen. The right approach is to let VMD run normally
# and just keep its stdin from hitting EOF (which would cause it to
# exit immediately under a non-interactive Ray job).
#
# We give VMD a stdin pipe that we never write to and never close. VMD
# sees an open stdin, runs its full event loop (mouse + Tk + redraw),
# and only exits when the user closes the OpenGL display window.
cmd = [VMD_CMD, FILENAME]
logging.info("[vmd_job] launching: %s on DISPLAY=%s", " ".join(cmd), DISPLAY)
proc = subprocess.Popen(cmd, env=env, stdin=subprocess.PIPE)
rc = proc.wait()
logging.info("[vmd_job] VMD exited with code %s", rc)
sys.exit(rc)
"""


def visualize(file_path: Path, label: str = "") -> None:
    """Send `file_path` to the Ray container and open it in VMD on XPRA.
    Blocks until VMD is closed (i.e. the Ray job finishes)."""
    if not PAUSE_FOR_VISUALIZATION:
        return

    file_path = Path(file_path)
    if not file_path.exists():
        logger.warning("  [visualize] file not found, skipping: %s", file_path)
        return

    logger.info(
        ">>> Visualizing %s%s on XPRA display - close VMD to continue...",
        file_path.name,
        f" ({label})" if label else "",
    )

    client = JobSubmissionClient(RAY_JOBS_ADDRESS)

    # Build a throwaway working_dir containing the structure file + entrypoint.
    with tempfile.TemporaryDirectory(prefix="vmd_job_") as tmp:
        tmp_path = Path(tmp)
        shutil.copy2(file_path, tmp_path / file_path.name)

        entry = _ENTRYPOINT_TEMPLATE.format(
            filename=file_path.name,
            display=XPRA_DISPLAY,
            vmd_cmd=VMD_COMMAND,
        )
        (tmp_path / "vmd_entry.py").write_text(entry)

        job_id = client.submit_job(
            entrypoint="python vmd_entry.py",
            runtime_env={"working_dir": str(tmp_path)},
        )
        logger.info("  [visualize] submitted job %s", job_id)

        terminal = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}
        while True:
            status = client.get_job_status(job_id)
            if status in terminal:
                break
            time.sleep(1.0)

        if status != JobStatus.SUCCEEDED:
            logs = client.get_job_logs(job_id)
            logger.error("  [visualize] job %s ended as %s", job_id, status)
            if logs:
                logger.error("%s", logs)

    logger.info(">>> Resumed.")
