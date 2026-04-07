"""
Step 1: Generate receptor topology and convert ligand to .gro format.

Corresponds to tutorial lines 121-131:
  - gmx pdb2gmx -f REC.pdb -ignh  (select CHARMM27 + TIP3P)
  - gmx editconf -f LIG.pdb -o LIG.gro
  - Merge LIG.gro atom lines into conf.gro (produced by pdb2gmx)

Prerequisites (user has already done manually):
  - REC.pdb, LIG.pdb, LIG.itp, all .mdp files, and the force field
    directory are present in SIM_DIR.
"""

import sys

from research_work.config import SIM_DIR, RECEPTOR_PDB
from research_work.utils.gmx import run_gmx
from research_work.utils.file_edit import merge_gro_files


def verify_inputs():
    """Check that all required files exist in SIM_DIR before starting."""
    required = [
        RECEPTOR_PDB,
        "LIG.pdb",
        "LIG.itp",
    ]
    missing = [f for f in required if not (SIM_DIR / f).exists()]
    if missing:
        print(f"ERROR: Missing files in {SIM_DIR}:")
        for f in missing:
            print(f"  - {f}")
        print("\nMake sure you've completed the manual Chimera/SwissParam prep")
        print("and copied everything into the simulation folder.")
        sys.exit(1)


def run_pdb2gmx():
    """
    gmx pdb2gmx -f REC.pdb -ignh
    Runs interactively so the user can select force field and water model.
    Produces: conf.gro, topol.top, posre.itp
    """
    print("  Select the force field and water model when prompted.")
    run_gmx(
        "pdb2gmx",
        ["-f", RECEPTOR_PDB, "-ignh"],
        interactive=True,
        work_dir=SIM_DIR,
    )
    print("  -> Produced: conf.gro, topol.top, posre.itp")


def convert_ligand_to_gro():
    """
    gmx editconf -f LIG.pdb -o LIG.gro
    """
    run_gmx(
        "editconf",
        ["-f", "LIG.pdb", "-o", "LIG.gro"],
        work_dir=SIM_DIR,
    )
    print("  -> Produced: LIG.gro")


def merge_ligand_into_conf():
    """Merge LIG.gro atom lines into conf.gro."""
    merge_gro_files(SIM_DIR / "conf.gro", SIM_DIR / "LIG.gro")


def run():
    print("\n" + "=" * 60)
    print("STEP 1: Receptor Topology & Ligand Conversion")
    print("=" * 60)

    verify_inputs()

    print("\n[1a] Running pdb2gmx on receptor...")
    run_pdb2gmx()

    print("\n[1b] Converting LIG.pdb to LIG.gro...")
    convert_ligand_to_gro()

    print("\n[1c] Merging ligand atoms into conf.gro...")
    merge_ligand_into_conf()

    print("\nStep 1 complete.")


if __name__ == "__main__":
    run()
