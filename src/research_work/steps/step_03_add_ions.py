"""
Step 3: Add ions to neutralize the solvated system.

Corresponds to tutorial lines 180-193:
  - gmx grompp -f ions.mdp -c box_sol.gro -p topol.top -o ION.tpr
      (pauses for user review if warnings are emitted)
  - gmx genion -s ION.tpr -p topol.top -conc 0.1 -neutral -o box_sol_ion.gro
      (select SOL group, e.g. "15")
"""

import logging
import time

from research_work.config import SIM_DIR, MDP_FILES, ION_CONCENTRATION, GENION_GROUP, MAXWARN
from research_work.utils import console
from research_work.utils.check_step import check_step
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_ions(detach: bool = False):
    check_step(
        "grompp",
        ["-f", MDP_FILES["ions"], "-c", "box_sol.gro", "-p", "topol.top", "-o", "ION.tpr"],
        work_dir=SIM_DIR,
        default_maxwarn=MAXWARN,
        detach=detach,
    )
    console.produced("ION.tpr")


def genion():
    run_gmx(
        "genion",
        ["-s", "ION.tpr", "-p", "topol.top", "-conc", ION_CONCENTRATION, "-neutral", "-o", "box_sol_ion.gro"],
        stdin_lines=[GENION_GROUP],
        work_dir=SIM_DIR,
    )
    console.produced("box_sol_ion.gro")


def run(detach: bool = False):
    start = console.step_header(3, "Add Ions (Neutralize System)")

    console.substep("3a", "Assembling ION.tpr (gmx grompp)")
    grompp_ions(detach=detach)

    console.substep("3b", "Replacing solvent with ions (gmx genion)")
    genion()

    console.step_done(time.monotonic() - start)
    if not detach:
        visualize(SIM_DIR / "box_sol_ion.gro", label="after genion")


if __name__ == "__main__":
    run()
