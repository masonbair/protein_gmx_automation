"""
File editing utilities for GROMACS input files.

Handles .gro merging and .top/.itp edits.
"""

from pathlib import Path


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
    print(f"  Merged {insert_natoms} atoms from {insert_gro.name} into {base_gro.name} "
          f"(total: {total_atoms})")


# ─── .top file operations ────────────────────────────────────────────

def add_ligand_posres_include(top_path: Path, itp_name: str = "posre_LIG.itp"):
    """
    Append a ligand position-restraint #ifdef POSRES block to topol.top.
    Idempotent — does nothing if the include is already present.
    """
    content = top_path.read_text()
    if itp_name in content:
        print(f"  '{itp_name}' include already present in {top_path.name}, skipping.")
        return

    block = (
        "\n; Ligand position restraints\n"
        "#ifdef POSRES\n"
        f'#include "{itp_name}"\n'
        "#endif\n"
    )
    top_path.write_text(content.rstrip("\n") + "\n" + block)
    print(f"  Added ligand POSRES include ({itp_name}) to {top_path.name}")


def append_to_molecules_section(top_path: Path, molecule_name: str, count: int = 1):
    """
    Append a molecule entry (e.g. 'LIG          1') to the [ molecules ] section
    at the bottom of a .top file.
    """
    content = top_path.read_text()
    entry = f"{molecule_name:<20s} {count}\n"
    content = content.rstrip("\n") + "\n" + entry
    top_path.write_text(content)
    print(f"  Appended '{molecule_name} {count}' to [ molecules ] in {top_path.name}")
