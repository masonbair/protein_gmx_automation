"""
Step 8: Production MD run.

  - gmx grompp -f MD.mdp -c NPT.gro -t NPT.cpt -p topol.top -n index.ndx -o MD.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm MD -v

To resume an interrupted production run, use:
    gmx mdrun -s MD.tpr -cpi MD.cpt -deffnm MD -append -v

Detached mode: the parent pipeline spawns `python -m
research_work.steps.step_08_production_md --detached-run` in the
background. That child runs mdrun synchronously and, on success, fires
the final VMD visualization on the XPRA display.
"""

import argparse
import logging
import subprocess
import sys

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_md(detach: bool = False):
    check_step(
        "grompp",
        [
            "-f", MDP_FILES["md"],
            "-c", "NPT.gro",
            "-t", "NPT.cpt",
            "-p", "topol.top",
            "-n", "index.ndx",
            "-o", "MD.tpr",
        ],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )


def mdrun_md(detach: bool = False):
    """
    Production mdrun. If a checkpoint exists from a prior interrupted run,
    GROMACS users typically resume manually with:
        gmx mdrun -s MD.tpr -cpi MD.cpt -deffnm MD -append -v
    """
    if not detach:
        run_gmx("mdrun", ["-deffnm", "MD", "-v"], work_dir=SIM_DIR)
        logger.info("  -> Produced: MD.gro, MD.xtc, MD.edr, MD.cpt, MD.log")
        return

    logs_dir = SIM_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_path = logs_dir / "step8_mdrun.out"
    err_path = logs_dir / "step8_mdrun.err"
    pid_path = logs_dir / "step8_mdrun.pid"

    # Spawn a python wrapper (this same module, --detached-run) instead
    # of gmx directly. The wrapper runs mdrun synchronously, then fires
    # the final visualization once mdrun finishes.
    cmd = [sys.executable, "-m", "research_work.steps.step_08_production_md", "--detached-run"]
    logger.info("Launching detached wrapper: %s", " ".join(cmd))

    with open(out_path, "a", encoding="utf-8") as out_f, open(err_path, "a", encoding="utf-8") as err_f:
        proc = subprocess.Popen(
            cmd,
            cwd=SIM_DIR,
            stdin=subprocess.DEVNULL,
            stdout=out_f,
            stderr=err_f,
            start_new_session=True,
        )

    pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")
    logger.info("Detached step 8 wrapper started with PID %s", proc.pid)
    logger.info("mdrun stdout: %s", out_path)
    logger.info("mdrun stderr: %s", err_path)
    logger.info("pid file:     %s", pid_path)


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 8: Production MD")
    logger.info("%s", "=" * 60)

    logger.info("[8a] Assembling MD.tpr with grompp...")
    grompp_md(detach=detach)

    logger.info("[8b] Running production MD (this may take a while)...")
    mdrun_md(detach=detach)

    if detach:
        logger.info("Step 8 launched in detached mode.")
        logger.info("Production MD is running in the background - it has NOT finished yet.")
        logger.info("Check progress with: python -m research_work.status")
        logger.info("When mdrun completes, the final trajectory will be opened in VMD automatically.")
        return

    logger.info("Step 8 complete - production run finished.")
    logger.info("Launching final visualization of the production trajectory...")
    visualize(SIM_DIR / "MD.gro", label="final production MD")


def _detached_run():
    """
    Entry point for the detached wrapper process.

    The parent pipeline spawns this via
        python -m research_work.steps.step_08_production_md --detached-run
    with stdout/stderr redirected to step8_mdrun.{out,err} and stdin set
    to /dev/null. We run mdrun synchronously (streaming output so the
    user can tail the log in real time), then fire the final VMD
    visualization with force=True so the user gets the completion cue
    even if PAUSE_FOR_VISUALIZATION is False.
    """
    from research_work.utils.logging_setup import setup_logging

    log_file = setup_logging(SIM_DIR / "logs")
    logger.info("%s", "=" * 60)
    logger.info("STEP 8 [detached]: Production MD (background wrapper)")
    logger.info("%s", "=" * 60)
    logger.info("Detached runner log: %s", log_file)

    try:
        run_gmx(
            "mdrun",
            ["-deffnm", "MD", "-v"],
            work_dir=SIM_DIR,
            stream_output=True,
        )
        logger.info("  -> Produced: MD.gro, MD.xtc, MD.edr, MD.cpt, MD.log")
    except SystemExit:
        logger.error("mdrun failed in detached mode - skipping visualization.")
        raise

    logger.info("Detached mdrun complete - launching final visualization...")
    visualize(SIM_DIR / "MD.gro", label="final production MD (detached)", force=True)
    logger.info("Detached step 8 finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 8: Production MD")
    parser.add_argument(
        "--detached-run",
        action="store_true",
        help="Internal flag: run mdrun synchronously then visualize. "
             "Used by the parent pipeline when launching the background worker.",
    )
    args = parser.parse_args()
    if args.detached_run:
        _detached_run()
    else:
        run()
