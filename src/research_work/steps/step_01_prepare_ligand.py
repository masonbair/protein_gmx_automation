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

import logging
import sys
import time

from research_work.config import (
    SIM_DIR,
    RECEPTOR_PDB,
    DETACH_PDB2GMX_FORCEFIELD,
    DETACH_PDB2GMX_WATER,
)
from research_work.utils import console
from research_work.utils.gmx import run_gmx
from research_work.utils.file_edit import merge_gro_files


logger = logging.getLogger(__name__)


def verify_inputs():
    """Check that all required files exist in SIM_DIR before starting."""
    required = [RECEPTOR_PDB, "LIG.pdb", "LIG.itp"]
    missing = [f for f in required if not (SIM_DIR / f).exists()]
    if missing:
        logger.error("Missing files in %s:", SIM_DIR)
        for f in missing:
            logger.error("  - %s", f)
        logger.error("Make sure you've completed the manual Chimera/SwissParam prep")
        logger.error("and copied everything into the simulation folder.")
        sys.exit(1)


def run_pdb2gmx(detach: bool = False):
    if detach:
        console.info(f"[detach] force field={DETACH_PDB2GMX_FORCEFIELD}, water={DETACH_PDB2GMX_WATER} (from config)")
        run_gmx(
            "pdb2gmx",
            ["-f", RECEPTOR_PDB, "-ignh"],
            stdin_lines=[DETACH_PDB2GMX_FORCEFIELD, DETACH_PDB2GMX_WATER],
            work_dir=SIM_DIR,
        )
    else:
        console.hint("Select the force field and water model when prompted.")
        run_gmx(
            "pdb2gmx",
            ["-f", RECEPTOR_PDB, "-ignh"],
            interactive=True,
            work_dir=SIM_DIR,
        )
    console.produced("conf.gro, topol.top, posre.itp")


def convert_ligand_to_gro():
    run_gmx("editconf", ["-f", "LIG.pdb", "-o", "LIG.gro"], work_dir=SIM_DIR)
    console.produced("LIG.gro")


def merge_ligand_into_conf():
    merge_gro_files(SIM_DIR / "conf.gro", SIM_DIR / "LIG.gro")


def run(detach: bool = False):
    start = console.step_header(1, "Receptor Topology & Ligand Conversion")

    verify_inputs()

    console.substep("1a", "Building receptor topology (gmx pdb2gmx)")
    run_pdb2gmx(detach=detach)

    console.substep("1b", "Converting LIG.pdb to GROMACS format (gmx editconf)")
    convert_ligand_to_gro()

    console.substep("1c", "Merging ligand atoms into conf.gro")
    merge_ligand_into_conf()

    console.step_done(time.monotonic() - start)


if __name__ == "__main__":
    run()
