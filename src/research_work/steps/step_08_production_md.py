"""
Step 8: Production MD run.

  - gmx grompp -f MD.mdp -c NPT.gro -t NPT.cpt -p topol.top -n index.ndx -o MD.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm MD -v

To resume an interrupted production run, use:
    gmx mdrun -s MD.tpr -cpi MD.cpt -deffnm MD -append -v
"""

import logging
import subprocess

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_md():
    base_args = [
        "-f", MDP_FILES["md"],
        "-c", "NPT.gro",
        "-t", "NPT.cpt",
        "-p", "topol.top",
        "-n", "index.ndx",
        "-o", "MD.tpr",
    ]
    result = run_gmx("grompp", base_args, work_dir=SIM_DIR, check=False)
    if result.returncode == 0:
        return
    if "warning" in (result.stderr or "").lower():
        logger.warning("  grompp failed with warnings - retrying with -maxwarn %s.", MAXWARN)
        run_gmx("grompp", base_args, work_dir=SIM_DIR, maxwarn=MAXWARN)
    else:
        logger.error("grompp failed for reasons other than warnings.")
        raise SystemExit(1)


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

    cmd = ["gmx", "mdrun", "-deffnm", "MD", "-v"]
    logger.info("Launching detached process: %s", " ".join(cmd))

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
    logger.info("Detached step 8 started with PID %s", proc.pid)
    logger.info("stdout log: %s", out_path)
    logger.info("stderr log: %s", err_path)
    logger.info("pid file: %s", pid_path)


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 8: Production MD")
    logger.info("%s", "=" * 60)

    logger.info("[8a] Assembling MD.tpr with grompp...")
    grompp_md()

    logger.info("[8b] Running production MD (this may take a while)...")
    mdrun_md(detach=detach)

    if detach:
        logger.info("Step 8 launched in detached mode. Exiting without visualization.")
        return

    logger.info("Step 8 complete - production run finished.")
    logger.info("Launching final visualization of the production trajectory...")
    visualize(SIM_DIR / "MD.gro", label="final production MD")


if __name__ == "__main__":
    run()
