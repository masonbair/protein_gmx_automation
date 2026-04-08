"""
Step 4: Energy Minimization.

Corresponds to tutorial lines 195-201:
  - gmx grompp -f EM.mdp -c box_sol_ion.gro -p topol.top -o EM.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -v -deffnm EM
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_em():
    """
    Try grompp without -maxwarn first. If it fails because of warnings,
    retry once with -maxwarn from config so the user sees the warnings
    but still moves forward.
    """
    base_args = [
        "-f", MDP_FILES["em"],
        "-c", "box_sol_ion.gro",
        "-p", "topol.top",
        "-o", "EM.tpr",
    ]

    result = run_gmx("grompp", base_args, work_dir=SIM_DIR, check=False)
    if result.returncode == 0:
        return

    stderr = (result.stderr or "")
    if "warning" in stderr.lower():
        logger.warning("  grompp failed with warnings - retrying with -maxwarn %s.", MAXWARN)
        logger.warning("  (Review the warnings above to confirm they are acceptable.)")
        run_gmx("grompp", base_args, work_dir=SIM_DIR, maxwarn=MAXWARN)
    else:
        logger.error("grompp failed for reasons other than warnings. See output above.")
        raise SystemExit(1)


def mdrun_em():
    """gmx mdrun -v -deffnm EM"""
    run_gmx(
        "mdrun",
        ["-v", "-deffnm", "EM"],
        work_dir=SIM_DIR,
    )
    logger.info("  -> Produced: EM.gro, EM.edr, EM.log, EM.trr")


def run():
    logger.info("%s", "=" * 60)
    logger.info("STEP 4: Energy Minimization")
    logger.info("%s", "=" * 60)

    logger.info("[4a] Assembling EM.tpr with grompp...")
    grompp_em()

    logger.info("[4b] Running energy minimization (mdrun)...")
    mdrun_em()

    logger.info("Step 4 complete.")
    visualize(SIM_DIR / "EM.gro", label="after energy minimization")


if __name__ == "__main__":
    run()
