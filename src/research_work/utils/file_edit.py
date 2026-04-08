"""
File editing utilities for GROMACS input files.

Handles .gro merging and .top/.itp edits.
"""

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


# ─── .gro file operations ───────────────────────────────────────────

def merge_gro_files(base_gro: Path, insert_gro: Path):
    """
    Merge atom lines from insert_gro into base_gro.

    .gro format:
      Line 1: title
      Line 2: number of atoms
      Lines 3..N+2: atom lines (fixed-width columns)
      Last line: box vectors

    Inserts the atom lines from insert_gro before the box vector line
    in base_gro and updates the atom count. Edits base_gro in-place.
    """
    base_lines = base_gro.read_text().splitlines()
    insert_lines = insert_gro.read_text().splitlines()

    # Parse base .gro
    base_title = base_lines[0]
    base_natoms = int(base_lines[1].strip())
    base_atom_lines = base_lines[2:2 + base_natoms]
    base_box = base_lines[2 + base_natoms]  # last line = box vectors

    # Parse insert .gro
    insert_natoms = int(insert_lines[1].strip())
    insert_atom_lines = insert_lines[2:2 + insert_natoms]

    # Merge
    total_atoms = base_natoms + insert_natoms
    merged = (
        [base_title]
        + [f"{total_atoms:>5d}"]
        + base_atom_lines
        + insert_atom_lines
        + [base_box]
    )

    base_gro.write_text("\n".join(merged) + "\n")
    logger.info(
        "  Merged %s atoms from %s into %s (total: %s)",
        insert_natoms,
        insert_gro.name,
        base_gro.name,
        total_atoms,
    )


# ─── .top file operations ────────────────────────────────────────────

def add_ligand_posres_include(lig_itp_path: Path, itp_name: str = "posre_LIG.itp"):
    """
    Append a ligand position-restraint #ifdef POSRES block to LIG.itp.

    The include MUST live inside the ligand [moleculetype] block so grompp
    resolves the atom indices against ligand atoms. LIG.itp typically
    contains only the single LIG moleculetype, so appending at end-of-file
    is still inside that moleculetype's scope and is the safe placement.

    Putting this block in topol.top instead (after [ system ] / [ molecules ])
    causes grompp to error with:
        "Atom index (N) in position_restraints out of bounds (1-1)"

    Idempotent — does nothing if the include is already present.
    """
    content = lig_itp_path.read_text()
    if itp_name in content:
        logger.info("  '%s' include already present in %s, skipping.", itp_name, lig_itp_path.name)
        return

    block = (
        "\n; Ligand position restraints\n"
        "#ifdef POSRES\n"
        f'#include "{itp_name}"\n'
        "#endif\n"
    )
    lig_itp_path.write_text(content.rstrip("\n") + "\n" + block)
    logger.info("  Added ligand POSRES include (%s) to %s", itp_name, lig_itp_path.name)


def append_to_molecules_section(top_path: Path, molecule_name: str, count: int = 1):
    """
    Append a molecule entry (e.g. 'LIG          1') to the [ molecules ] section
    at the bottom of a .top file.
    """
    content = top_path.read_text()
    entry = f"{molecule_name:<20s} {count}\n"
    content = content.rstrip("\n") + "\n" + entry
    top_path.write_text(content)
    logger.info("  Appended '%s %s' to [ molecules ] in %s", molecule_name, count, top_path.name)
