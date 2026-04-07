"""
Step 3: Add ions to neutralize the solvated system.

Corresponds to tutorial lines 180-193:
  - gmx grompp -f ions.mdp -c box_sol.gro -p topol.top -o ION.tpr
  - gmx genion -s ION.tpr -p topol.top -conc 0.1 -neutral -o box_sol_ion.gro
      (select SOL group, e.g. "15")
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SIM_DIR, MDP_FILES, ION_CONCENTRATION, GENION_GROUP, MAXWARN
from utils.gmx import run_gmx
from utils.visualize import visualize


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
    print("  -> Produced: ION.tpr")


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
    print("  -> Produced: box_sol_ion.gro")


def run():
    print("\n" + "=" * 60)
    print("STEP 3: Add Ions (Neutralize System)")
    print("=" * 60)

    print("\n[3a] Assembling ION.tpr with grompp...")
    grompp_ions()

    print("\n[3b] Replacing solvent with ions (genion)...")
    genion()

    print("\nStep 3 complete.")
    visualize(SIM_DIR / "box_sol_ion.gro", label="after genion")


if __name__ == "__main__":
    run()
