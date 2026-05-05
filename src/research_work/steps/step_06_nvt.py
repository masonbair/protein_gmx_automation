"""
Step 6: NVT equilibration.

  - gmx grompp -f NVT.mdp -c EM.gro -r EM.gro -p topol.top -n index.ndx -o NVT.tpr
      (pauses for user review if warnings are emitted)
  - gmx mdrun -deffnm NVT
"""

import logging
import time

from research_work import config
from research_work.config import MDP_FILES, MAXWARN
from research_work.utils import console
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_nvt(detach: bool = False):
    check_step(
        "grompp",
        ["-f", MDP_FILES["nvt"], "-c", "EM.gro", "-r", "EM.gro", "-p", "topol.top", "-n", "index.ndx", "-o", "NVT.tpr"],
        work_dir=config.SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )
    console.produced("NVT.tpr")


def mdrun_nvt():
    run_gmx("mdrun", ["-deffnm", "NVT"], work_dir=config.SIM_DIR)
    console.produced("NVT.gro, NVT.edr, NVT.cpt, NVT.log, NVT.trr")


def run(detach: bool = False):
    start = console.step_header(6, "NVT Equilibration")

    console.substep("6a", "Assembling NVT.tpr (gmx grompp)")
    grompp_nvt(detach=detach)

    console.substep("6b", "Running NVT equilibration (gmx mdrun)")
    mdrun_nvt()

    console.step_done(time.monotonic() - start)


if __name__ == "__main__":
    run()
