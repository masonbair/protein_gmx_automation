"""
Step 4: Energy Minimization.

Corresponds to tutorial lines 195-201:
  - gmx grompp -f EM.mdp -c box_sol_ion.gro -p topol.top -o EM.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -v -deffnm EM
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_em(detach: bool = False):
    check_step(
        "grompp",
        [
            "-f", MDP_FILES["em"],
            "-c", "box_sol_ion.gro",
            "-p", "topol.top",
            "-o", "EM.tpr",
        ],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )


def mdrun_em():
    """gmx mdrun -v -deffnm EM"""
    run_gmx(
        "mdrun",
        ["-v", "-deffnm", "EM"],
        work_dir=SIM_DIR,
    )
    logger.info("  -> Produced: EM.gro, EM.edr, EM.log, EM.trr")


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 4: Energy Minimization")
    logger.info("%s", "=" * 60)

    logger.info("[4a] Assembling EM.tpr with grompp...")
    grompp_em(detach=detach)

    logger.info("[4b] Running energy minimization (mdrun)...")
    mdrun_em()

    logger.info("Step 4 complete.")
    if not detach:
        visualize(SIM_DIR / "EM.gro", label="after energy minimization")


if __name__ == "__main__":
    run()
