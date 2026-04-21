"""
Step 6: NVT equilibration.

  - gmx grompp -f NVT.mdp -c EM.gro -r EM.gro -p topol.top -n index.ndx -o NVT.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm NVT
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_nvt(detach: bool = False):
    check_step(
        "grompp",
        [
            "-f", MDP_FILES["nvt"],
            "-c", "EM.gro",
            "-r", "EM.gro",
            "-p", "topol.top",
            "-n", "index.ndx",
            "-o", "NVT.tpr",
        ],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )


def mdrun_nvt():
    run_gmx("mdrun", ["-deffnm", "NVT"], work_dir=SIM_DIR)
    logger.info("  -> Produced: NVT.gro, NVT.edr, NVT.cpt, NVT.log, NVT.trr")


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 6: NVT Equilibration")
    logger.info("%s", "=" * 60)

    logger.info("[6a] Assembling NVT.tpr with grompp...")
    grompp_nvt(detach=detach)

    logger.info("[6b] Running NVT equilibration (mdrun)...")
    mdrun_nvt()

    logger.info("Step 6 complete.")


if __name__ == "__main__":
    run()
