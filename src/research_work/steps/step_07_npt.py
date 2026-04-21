"""
Step 7: NPT equilibration.

  - gmx grompp -f NPT.mdp -c NVT.gro -r NVT.gro -p topol.top -n index.ndx -o NPT.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm NPT
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_npt(detach: bool = False):
    check_step(
        "grompp",
        [
            "-f", MDP_FILES["npt"],
            "-c", "NVT.gro",
            "-r", "NVT.gro",
            "-p", "topol.top",
            "-n", "index.ndx",
            "-o", "NPT.tpr",
        ],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )


def mdrun_npt():
    run_gmx("mdrun", ["-deffnm", "NPT"], work_dir=SIM_DIR)
    logger.info("  -> Produced: NPT.gro, NPT.edr, NPT.cpt, NPT.log, NPT.trr")


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 7: NPT Equilibration")
    logger.info("%s", "=" * 60)

    logger.info("[7a] Assembling NPT.tpr with grompp...")
    grompp_npt(detach=detach)

    logger.info("[7b] Running NPT equilibration (mdrun)...")
    mdrun_npt()

    logger.info("Step 7 complete.")


if __name__ == "__main__":
    run()
