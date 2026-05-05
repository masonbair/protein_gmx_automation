"""
Step 7: NPT equilibration.

  - gmx grompp -f NPT.mdp -c NVT.gro -r NVT.gro -p topol.top -n index.ndx -o NPT.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm NPT
"""

import logging
import time

from research_work import config
from research_work.config import MDP_FILES, MAXWARN
from research_work.utils import console
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_npt(detach: bool = False):
    check_step(
        "grompp",
        ["-f", MDP_FILES["npt"], "-c", "NVT.gro", "-r", "NVT.gro", "-p", "topol.top", "-n", "index.ndx", "-o", "NPT.tpr"],
        work_dir=config.SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )
    console.produced("NPT.tpr")


def mdrun_npt():
    run_gmx("mdrun", ["-deffnm", "NPT"], work_dir=config.SIM_DIR)
    console.produced("NPT.gro, NPT.edr, NPT.cpt, NPT.log, NPT.trr")


def run(detach: bool = False):
    start = console.step_header(7, "NPT Equilibration")

    console.substep("7a", "Assembling NPT.tpr (gmx grompp)")
    grompp_npt(detach=detach)

    console.substep("7b", "Running NPT equilibration (gmx mdrun)")
    mdrun_npt()

    console.step_done(time.monotonic() - start)


if __name__ == "__main__":
    run()
