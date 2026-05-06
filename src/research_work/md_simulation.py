"""
Main entry point for the GROMACS MD simulation pipeline.

Usage:
    run-md <sim_dir>                 # Run all steps interactively
    run-md .                         # Use current directory as sim_dir
    run-md simulation/               # Use relative path
    run-md --step 1 <sim_dir>        # Run only step 1
    run-md --from 3 <sim_dir>        # Resume from step 3 onward
    run-md --no-visualize <sim_dir>  # Skip all VMD visualization pauses
    run-md --windows <sim_dir>       # Use local-VMD backend (no Ray/XPRA)
    run-md --detach-step8 <sim_dir>  # Run step 8 mdrun in the background
    run-md --detach <sim_dir>        # Full detached run: fork into the
                                     # background, feed config values to
                                     # every interactive prompt, skip VMD
                                     # pauses, and launch step 8 in its
                                     # own background process. The parent
                                     # shell returns immediately; logs
                                     # are written to <sim_dir>/logs.
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from research_work import config
from research_work.steps.step_01_prepare_ligand import run as step_01
from research_work.steps.step_02_edit_topology import run as step_02
from research_work.steps.step_03_add_ions import run as step_03
from research_work.steps.step_04_energy_min import run as step_04
from research_work.steps.step_05_restraints_index import run as step_05
from research_work.steps.step_06_nvt import run as step_06
from research_work.steps.step_07_npt import run as step_07
from research_work.steps.step_08_production_md import run as step_08
from research_work.utils.logging_setup import setup_logging


STEPS = {
    1: ("Receptor Topology & Ligand Conversion", step_01),
    2: ("Edit Topology & ITP Files",             step_02),
    3: ("Solvate & Add Ions",                    step_03),
    4: ("Energy Minimization",                   step_04),
    5: ("Restraints & System Index",             step_05),
    6: ("NVT Equilibration",                     step_06),
    7: ("NPT Equilibration",                     step_07),
    8: ("Production MD",                         step_08),
    # 9: ("Post-MD Analysis",                     step_09),
}


# Internal flag name used by the detach respawn. `--detached-runner` means
# "we're already the background copy, don't fork again." argparse turns
# dashes into underscores, so the attribute is args.detached_runner.
DETACHED_RUNNER_FLAG = "--detached-runner"


logger = logging.getLogger(__name__)


def _invoke(step_num: int, func, detach: bool, detach_step8: bool) -> None:
    """Call a step with the right kwargs. Step 8 accepts detach independently
    (so --detach-step8 works without --detach); every step accepts detach."""
    if step_num == 8:
        func(detach=(detach or detach_step8))
    else:
        func(detach=detach)


def _respawn_detached(argv_tail: list[str]) -> None:
    """Fork the current invocation into a background process and return.

    The child is detached (new session, DEVNULL stdin, stdout/stderr
    redirected to pipeline_detached_*.out/.err under SIM_DIR/logs) and
    carries the --detached-runner flag so it does not fork again.
    """
    logs_dir = config.SIM_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bg_out = logs_dir / f"pipeline_detached_{ts}.out"
    bg_err = logs_dir / f"pipeline_detached_{ts}.err"
    pid_path = logs_dir / "pipeline.pid"

    # -u forces unbuffered stdout/stderr so `tail -f` on the log file
    # shows progress in real time instead of waiting on the block buffer.
    cmd = [sys.executable, "-u", "-m", "research_work.run_md", *argv_tail, DETACHED_RUNNER_FLAG]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # start_new_session is POSIX-only; Windows needs CREATE_NEW_PROCESS_GROUP.
    popen_kwargs: dict = {}
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    with open(bg_out, "w", encoding="utf-8") as out_f, open(bg_err, "w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=out_f,
            stderr=err_f,
            env=env,
            **popen_kwargs,
        )

    pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")

    # Terminal output that the user sees in their shell — kept short on
    # purpose; everything the pipeline itself prints goes into the files.
    print("Pipeline launched in detached mode.")
    print(f"  PID file:       {pid_path}  (pid={proc.pid})")
    print(f"  pipeline log:   {bg_out}")
    print(f"  pipeline errs:  {bg_err}")
    print(f"  simulation dir: {config.SIM_DIR}")
    print(f"Check progress with: python -m research_work.status {config.SIM_DIR}")


def main():
    parser = argparse.ArgumentParser(description="GROMACS MD Simulation Pipeline")
    parser.add_argument(
        "sim_dir",
        metavar="sim_dir",
        help=(
            "Path to the simulation directory containing all input files "
            "(REC.pdb, LIG.pdb, LIG.itp, .mdp files, force field dir). "
            "Use '.' for the current directory."
        ),
    )
    parser.add_argument("--step", type=int, help="Run only this step")
    parser.add_argument("--from", dest="from_step", type=int, help="Start from this step")
    parser.add_argument(
        "--detach-step8",
        action="store_true",
        help="Launch step 8 production mdrun in the background and exit.",
    )
    parser.add_argument(
        "--detach",
        action="store_true",
        help=(
            "Run the entire pipeline in the background. Forks itself, "
            "redirects output to <sim_dir>/logs, feeds DETACH_* values from "
            "config.py to interactive prompts, skips VMD pauses, and "
            "launches step 8 mdrun as its own background process. Check "
            "progress with: python -m research_work.status <sim_dir>"
        ),
    )
    parser.add_argument(
        "--windows",
        action="store_true",
        help=(
            "Run in Windows / PowerShell mode: use the local-VMD "
            "visualization backend (no Ray/XPRA) and Windows-compatible "
            "subprocess flags for detached spawns."
        ),
    )
    parser.add_argument(
        "--no-visualize",
        action="store_true",
        dest="no_visualize",
        help="Skip all VMD visualization pauses during the run.",
    )
    parser.add_argument(
        "--detached-runner",
        action="store_true",
        dest="detached_runner",
        help=argparse.SUPPRESS,  # internal: set on the forked child only
    )
    args = parser.parse_args()

    # Resolve and validate sim_dir, then store it in the shared config so all
    # modules see it. Must happen before any step runs.
    sim_dir = Path(args.sim_dir).expanduser().resolve()
    if not sim_dir.is_dir():
        parser.error(f"sim_dir does not exist or is not a directory: {sim_dir}")
    config.SIM_DIR = sim_dir

    if args.windows:
        config.WINDOWS_MODE = True
    if args.no_visualize:
        config.PAUSE_FOR_VISUALIZATION = False

    # Parent side of --detach: respawn ourselves in the background and
    # return. Everything below this point runs only in the interactive
    # invocation or inside the detached child.
    if args.detach and not args.detached_runner:
        # Rebuild the child's argv from the user's, minus the bare
        # program name. `--detach` stays so the child knows to run in
        # detach mode (feed config values, skip pauses, detach step 8).
        _respawn_detached(sys.argv[1:])
        return

    log_file = setup_logging(config.SIM_DIR / "logs")
    print(f"  Log file: {log_file}")
    if args.detach:
        logger.info("Detached pipeline runner started (PID %s).", os.getpid())

    step_8_detached = False

    if args.step:
        if args.step not in STEPS:
            logger.error("Unknown step %s. Available: %s", args.step, list(STEPS.keys()))
            sys.exit(1)
        _invoke(args.step, STEPS[args.step][1], args.detach, args.detach_step8)
        if args.step == 8 and (args.detach or args.detach_step8):
            step_8_detached = True
    else:
        start = args.from_step or 1
        for step_num in sorted(STEPS.keys()):
            if step_num < start:
                continue
            _invoke(step_num, STEPS[step_num][1], args.detach, args.detach_step8)
            if step_num == 8 and (args.detach or args.detach_step8):
                step_8_detached = True

    print()
    if step_8_detached:
        print("Pipeline foreground steps complete.")
        print("Step 8 (production MD) is running in the background -- NOT done yet.")
        print(f"Check progress with: python -m research_work.status {config.SIM_DIR}")
    else:
        print("Pipeline complete.")


if __name__ == "__main__":
    main()
