"""
Step 2: Edit topology files and create simulation box.

Corresponds to tutorial lines 135-171:
  - Edit topol.top: add #include "LIG.itp" below forcefield include
  - Edit topol.top: add 'LIG 1' to [ molecules ] section
  - Edit lig.itp: rename moleculetype to LIG if needed
  - gmx editconf: create triclinic box around the system
"""

import logging
import re
import sys
import time

from research_work.config import SIM_DIR, LIGAND_NAME, BOX_DISTANCE, BOX_TYPE
from research_work.utils import console
from research_work.utils.gmx import run_gmx
from research_work.utils.file_edit import append_to_molecules_section
from research_work.utils.visualize import visualize


logger = logging.getLogger(__name__)


def edit_topol_add_ligand_include():
    top_path = SIM_DIR / "topol.top"
    lines = top_path.read_text().splitlines(keepends=True)

    insert_idx = None
    for i, line in enumerate(lines):
        if "#include" in line and "forcefield.itp" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        logger.error("Could not find forcefield #include in topol.top")
        sys.exit(1)

    remaining = "".join(lines[insert_idx:])
    if f'#include "{LIGAND_NAME}.itp"' in remaining:
        logger.info("topol.top already includes %s.itp, skipping.", LIGAND_NAME)
        return

    insert_block = (
        f"\n; Include ligand topology\n"
        f'#include "{LIGAND_NAME}.itp"\n'
    )
    lines.insert(insert_idx, insert_block)
    top_path.write_text("".join(lines))


def edit_topol_add_ligand_molecule():
    top_path = SIM_DIR / "topol.top"
    content = top_path.read_text()
    if re.search(rf"^{LIGAND_NAME}\s+1\s*$", content, re.MULTILINE):
        logger.info("topol.top already has '%s 1' in [ molecules ], skipping.", LIGAND_NAME)
        return
    append_to_molecules_section(top_path, LIGAND_NAME, count=1)


def edit_lig_itp():
    itp_path = SIM_DIR / "LIG.itp"
    if not itp_path.exists():
        itp_path = SIM_DIR / "lig.itp"
    if not itp_path.exists():
        logger.error("Neither LIG.itp nor lig.itp found in simulation folder.")
        sys.exit(1)

    content = itp_path.read_text()
    lines = content.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[ moleculetype ]") or stripped == "[moleculetype]":
            for j in range(i + 1, len(lines)):
                name_line = lines[j].strip()
                if not name_line or name_line.startswith(";"):
                    continue
                parts = name_line.split()
                current_name = parts[0]
                if current_name == LIGAND_NAME:
                    logger.info("%s moleculetype is already '%s', skipping.", itp_path.name, LIGAND_NAME)
                    return
                new_line = lines[j].replace(current_name, LIGAND_NAME, 1)
                lines[j] = new_line
                itp_path.write_text("\n".join(lines) + "\n")
                logger.info("Renamed moleculetype '%s' -> '%s' in %s", current_name, LIGAND_NAME, itp_path.name)
                return

    logger.error("Could not find [ moleculetype ] section in %s", itp_path.name)
    sys.exit(1)


def create_box():
    run_gmx(
        "editconf",
        ["-f", "conf.gro", "-d", BOX_DISTANCE, "-bt", BOX_TYPE, "-o", "box.gro"],
        work_dir=SIM_DIR,
    )
    console.produced("box.gro")


def solvate():
    run_gmx(
        "solvate",
        ["-cp", "box.gro", "-cs", "spc216.gro", "-p", "topol.top", "-o", "box_sol.gro"],
        work_dir=SIM_DIR,
    )
    console.produced("box_sol.gro")


def run(detach: bool = False):
    start = console.step_header(2, "Edit Topology, Create Box & Solvate")

    console.substep("2a", "Adding LIG.itp include to topol.top")
    edit_topol_add_ligand_include()

    console.substep("2b", "Adding LIG to [ molecules ] in topol.top")
    edit_topol_add_ligand_molecule()

    console.substep("2c", "Normalizing moleculetype name in LIG.itp")
    edit_lig_itp()

    console.substep("2d", "Creating simulation box (gmx editconf)")
    create_box()

    console.substep("2e", "Solvating the system (gmx solvate)")
    solvate()

    console.step_done(time.monotonic() - start)
    if not detach:
        visualize(SIM_DIR / "box_sol.gro", label="after solvate")


if __name__ == "__main__":
    run()
