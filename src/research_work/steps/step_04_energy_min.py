"""
Step 4: Energy Minimization.

Corresponds to tutorial lines 195-201:
  - gmx grompp -f EM.mdp -c box_sol_ion.gro -p topol.top -o EM.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm EM
"""

import logging
import time

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils import console
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_em(detach: bool = False):
    check_step(
        "grompp",
        ["-f", MDP_FILES["em"], "-c", "box_sol_ion.gro", "-p", "topol.top", "-o", "EM.tpr"],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )
    console.produced("EM.tpr")


def mdrun_em():
    run_gmx("mdrun", ["-deffnm", "EM"], work_dir=SIM_DIR)
    console.produced("EM.gro, EM.edr, EM.log, EM.trr")


def run(detach: bool = False):
    start = console.step_header(4, "Energy Minimization")

    console.substep("4a", "Assembling EM.tpr (gmx grompp)")
    grompp_em(detach=detach)

    console.substep("4b", "Running energy minimization (gmx mdrun)")
    mdrun_em()

    console.step_done(time.monotonic() - start)
    if not detach:
        visualize(SIM_DIR / "EM.gro", label="after energy minimization")


if __name__ == "__main__":
    run()
