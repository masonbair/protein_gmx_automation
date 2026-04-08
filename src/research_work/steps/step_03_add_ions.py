"""
Step 3: Add ions to neutralize the solvated system.

Corresponds to tutorial lines 180-193:
  - gmx grompp -f ions.mdp -c box_sol.gro -p topol.top -o ION.tpr
  - gmx genion -s ION.tpr -p topol.top -conc 0.1 -neutral -o box_sol_ion.gro
      (select SOL group, e.g. "15")
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, ION_CONCENTRATION, GENION_GROUP, MAXWARN
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def grompp_ions():
    """
    gmx grompp -f ions_NN.mdp -c box_sol.gro -p topol.top -maxwarn 2 -o ION.tpr
    """
    run_gmx(
        "grompp",
        [
            "-f", MDP_FILES["ions"],
            "-c", "box_sol.gro",
            "-p", "topol.top",
            "-o", "ION.tpr",
        ],
        work_dir=SIM_DIR,
        maxwarn=MAXWARN,
    )
    logger.info("  -> Produced: ION.tpr")


def genion():
    """
    gmx genion -s ION.tpr -p topol.top -conc 0.1 -neutral -o box_sol_ion.gro
    Select SOL group (default "15") for ion replacement.
    """
    run_gmx(
        "genion",
        [
            "-s", "ION.tpr",
            "-p", "topol.top",
            "-conc", ION_CONCENTRATION,
            "-neutral",
            "-o", "box_sol_ion.gro",
        ],
        stdin_lines=[GENION_GROUP],
        work_dir=SIM_DIR,
    )
    logger.info("  -> Produced: box_sol_ion.gro")


def run():
    logger.info("%s", "=" * 60)
    logger.info("STEP 3: Add Ions (Neutralize System)")
    logger.info("%s", "=" * 60)

    logger.info("[3a] Assembling ION.tpr with grompp...")
    grompp_ions()

    logger.info("[3b] Replacing solvent with ions (genion)...")
    genion()

    logger.info("Step 3 complete.")
    visualize(SIM_DIR / "box_sol_ion.gro", label="after genion")


if __name__ == "__main__":
    run()
