"""
Step 2: Edit topology files and create simulation box.

Corresponds to tutorial lines 135-171:
  - Edit topol.top: add #include "LIG.itp" below forcefield include
  - Edit topol.top: add 'LIG 1' to [ molecules ] section
  - Edit lig.itp: rename moleculetype to LIG if needed
  - gmx editconf: create triclinic box around the system
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SIM_DIR, LIGAND_NAME, BOX_DISTANCE, BOX_TYPE
from utils.gmx import run_gmx
from utils.file_edit import append_to_molecules_section


def edit_topol_add_ligand_include():
    """
    In topol.top, add:
        ; Include ligand topology
        #include "LIG.itp"
    right after the forcefield #include line.
    """
    top_path = SIM_DIR / "topol.top"
    lines = top_path.read_text().splitlines(keepends=True)

    # Find the forcefield include line (e.g. #include "charmm36-jul2022.ff/forcefield.itp")
    insert_idx = None
    for i, line in enumerate(lines):
        if "#include" in line and "forcefield.itp" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        print("ERROR: Could not find forcefield #include in topol.top")
        sys.exit(1)

    # Check if already added
    remaining = "".join(lines[insert_idx:])
    if f'#include "{LIGAND_NAME}.itp"' in remaining:
        print(f"  topol.top already includes {LIGAND_NAME}.itp, skipping.")
        return

    insert_block = (
        f"\n; Include ligand topology\n"
        f'#include "{LIGAND_NAME}.itp"\n'
    )
    lines.insert(insert_idx, insert_block)
    top_path.write_text("".join(lines))
    print(f"  Added #include \"{LIGAND_NAME}.itp\" to topol.top")


def edit_topol_add_ligand_molecule():
    """Add 'LIG 1' to the [ molecules ] section at the bottom of topol.top."""
    top_path = SIM_DIR / "topol.top"

    # Check if already present
    content = top_path.read_text()
    if re.search(rf"^{LIGAND_NAME}\s+1\s*$", content, re.MULTILINE):
        print(f"  topol.top already has '{LIGAND_NAME} 1' in [ molecules ], skipping.")
        return

    append_to_molecules_section(top_path, LIGAND_NAME, count=1)


def edit_lig_itp():
    """
    In LIG.itp (or lig.itp), ensure the [ moleculetype ] name is 'LIG'.
    The name varies between SwissParam outputs (e.g. 'lig_gmx2', 'UNK', etc.)
    so we find whatever is there and replace it.
    """
    # Try both casings
    itp_path = SIM_DIR / "LIG.itp"
    if not itp_path.exists():
        itp_path = SIM_DIR / "lig.itp"
    if not itp_path.exists():
        print("ERROR: Neither LIG.itp nor lig.itp found in simulation folder.")
        sys.exit(1)

    content = itp_path.read_text()
    lines = content.splitlines()

    # Find the [ moleculetype ] section and the name line after it
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[ moleculetype ]") or stripped == "[moleculetype]":
            # Skip comment lines to find the actual name line
            for j in range(i + 1, len(lines)):
                name_line = lines[j].strip()
                if not name_line or name_line.startswith(";"):
                    continue
                # This is the name line, e.g. "lig_gmx2   3"
                parts = name_line.split()
                current_name = parts[0]
                if current_name == LIGAND_NAME:
                    print(f"  {itp_path.name} moleculetype is already '{LIGAND_NAME}', skipping.")
                    return
                # Replace just the name, keep the nrexcl value
                new_line = lines[j].replace(current_name, LIGAND_NAME, 1)
                lines[j] = new_line
                itp_path.write_text("\n".join(lines) + "\n")
                print(f"  Renamed moleculetype '{current_name}' -> '{LIGAND_NAME}' in {itp_path.name}")
                return

    print("ERROR: Could not find [ moleculetype ] section in", itp_path.name)
    sys.exit(1)


def create_box():
    """
    gmx editconf -f conf.gro -d 1.0 -bt triclinic -o box.gro
    """
    run_gmx(
        "editconf",
        ["-f", "conf.gro", "-d", BOX_DISTANCE, "-bt", BOX_TYPE, "-o", "box.gro"],
        work_dir=SIM_DIR,
    )
    print("  -> Produced: box.gro")


def solvate():
    """
    gmx solvate -cp box.gro -cs spc216.gro -p topol.top -o box_sol.gro
    """
    run_gmx(
        "solvate",
        ["-cp", "box.gro", "-cs", "spc216.gro", "-p", "topol.top", "-o", "box_sol.gro"],
        work_dir=SIM_DIR,
    )
    print("  -> Produced: box_sol.gro")


def run():
    print("\n" + "=" * 60)
    print("STEP 2: Edit Topology, Create Box & Solvate")
    print("=" * 60)

    print("\n[2a] Adding ligand include to topol.top...")
    edit_topol_add_ligand_include()

    print("\n[2b] Adding ligand to [ molecules ] in topol.top...")
    edit_topol_add_ligand_molecule()

    print("\n[2c] Checking moleculetype name in LIG.itp...")
    edit_lig_itp()

    print("\n[2d] Creating simulation box...")
    create_box()

    print("\n[2e] Solvating the system...")
    solvate()

    print("\nStep 2 complete. Visualize box_sol.gro before continuing.")


if __name__ == "__main__":
    run()
