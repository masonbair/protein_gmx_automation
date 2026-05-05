"""
Visualization helper with two backends.

Linux / Ray path (default):
  Ships a single structure file to the remote `xrpa-ray-container` via
  the Ray Jobs API and launches VMD on the XPRA display (:80). The
  submitter runs OUTSIDE the container and talks to the Ray dashboard /
  Jobs API on port 8265. `visualize()` blocks until the job finishes,
  which happens when the user closes VMD.

Windows path (config.WINDOWS_MODE=True, set by `run_md.py --windows`):
  Skips Ray/XPRA entirely. Launches VMD locally via subprocess and
  blocks until the user closes the window. No container, no X display.
"""

import argparse
import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from research_work import config
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


def resolve_structure_path(path_arg: str) -> Path:
    """Resolve a structure path: first as-given, then relative to config.SIM_DIR."""
    candidate = Path(path_arg).expanduser()
    if candidate.exists():
        return candidate

    if config.SIM_DIR is not None:
        sim_candidate = (config.SIM_DIR / candidate).resolve()
        if sim_candidate.exists():
            return sim_candidate

    return candidate


def _visualize_windows(file_path: Path) -> None:
    """Launch VMD locally. Blocks until the user closes the VMD window."""
    cmd = [VMD_COMMAND, str(file_path)]
    logger.info("  [visualize/windows] launching: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        logger.error(
            "  [visualize/windows] %r not found on PATH - skipping visualization.",
            VMD_COMMAND,
        )
        return
    if result.returncode != 0:
        logger.warning("  [visualize/windows] VMD exited with code %s", result.returncode)


def _visualize_ray(file_path: Path) -> None:
    """Submit a Ray job that runs VMD on the XPRA display. Blocks on the job."""
    # Imported lazily so Windows users don't need the `ray` package installed.
    from ray.job_submission import JobStatus, JobSubmissionClient

    client = JobSubmissionClient(RAY_JOBS_ADDRESS)

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
        logger.info("  [visualize/ray] submitted job %s", job_id)

        terminal = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}
        while True:
            status = client.get_job_status(job_id)
            if status in terminal:
                break
            time.sleep(1.0)

        if status != JobStatus.SUCCEEDED:
            logs = client.get_job_logs(job_id)
            logger.error("  [visualize/ray] job %s ended as %s", job_id, status)
            if logs:
                logger.error("%s", logs)


def visualize(file_path: Path, label: str = "", force: bool = False) -> None:
    """Open `file_path` in VMD and block until the user closes it.

    Backend depends on config.WINDOWS_MODE: Ray/XPRA on Linux, direct
    subprocess on Windows.

    If `force` is True, the call runs regardless of PAUSE_FOR_VISUALIZATION —
    used by the detached step 8 wrapper so the final trajectory view always
    fires even when intermediate pauses were disabled for the run.
    """
    if not PAUSE_FOR_VISUALIZATION and not force:
        return

    file_path = Path(file_path)
    if not file_path.exists():
        logger.warning("  [visualize] file not found, skipping: %s", file_path)
        return

    backend = "windows" if config.WINDOWS_MODE else "XPRA display"
    logger.info(
        ">>> Visualizing %s%s on %s - close VMD to continue...",
        file_path.name,
        f" ({label})" if label else "",
        backend,
    )

    if config.WINDOWS_MODE:
        _visualize_windows(file_path)
    else:
        _visualize_ray(file_path)

    logger.info(">>> Resumed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualize a structure file in VMD through the Ray/XPRA setup."
    )
    parser.add_argument(
        "structure",
        help="Structure file to visualize (e.g. MD.gro or /path/to/MD.gro).",
    )
    parser.add_argument(
        "--label",
        default="",
        help="Optional label shown in logs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run visualization even if PAUSE_FOR_VISUALIZATION is False.",
    )
    args = parser.parse_args()

    if args.force:
        global PAUSE_FOR_VISUALIZATION
        PAUSE_FOR_VISUALIZATION = True

    structure_path = resolve_structure_path(args.structure)
    visualize(structure_path, label=args.label)


if __name__ == "__main__":
    main()
