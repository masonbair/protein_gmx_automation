"""
File editing utilities for GROMACS input files.

Handles mol2 cleanup, bond sorting, .gro merging, .top/.itp edits.
"""

from pathlib import Path


def clean_mol2_header(mol2_path: Path, molecule_name: str = "LIG"):
    """
    Clean a .mol2 file so that:
    1. @<TRIPOS>MOLECULE is the very first line (remove any preceding junk).
    2. The molecule name (line after @<TRIPOS>MOLECULE) is set to `molecule_name`.

    Edits the file in-place.
    """
    lines = mol2_path.read_text().splitlines(keepends=True)

    # Find the first @<TRIPOS>MOLECULE line
    start = None
    for i, line in enumerate(lines):
        if "@<TRIPOS>MOLECULE" in line:
            start = i
            break

    if start is None:
        raise ValueError(f"No @<TRIPOS>MOLECULE found in {mol2_path}")

    # Strip everything before it
    lines = lines[start:]

    # The molecule name is the line immediately after @<TRIPOS>MOLECULE
    if len(lines) < 2:
        raise ValueError(f"Unexpected end of file after @<TRIPOS>MOLECULE in {mol2_path}")

    lines[1] = molecule_name + "\n"

    mol2_path.write_text("".join(lines))
    print(f"  Cleaned header and set molecule name to '{molecule_name}' in {mol2_path.name}")


def sort_mol2_bonds(mol2_path: Path, output_path: Path | None = None):
    """
    Python port of sort_mol2_bonds.pl by Justin Lemkul.

    Reorders the @<TRIPOS>BOND section so that:
    1. Atoms on each bond line are in increasing order (e.g. 1 2, not 2 1).
    2. Bonds appear in order of ascending first atom number.
    3. For bonds with the same first atom, sorted by ascending second atom.

    If output_path is None, edits in-place.
    """
    if output_path is None:
        output_path = mol2_path

    lines = mol2_path.read_text().splitlines()

    # Ensure file starts with @<TRIPOS>
    if not lines[0].strip().startswith("@<TRIPOS>"):
        raise ValueError(
            f"Nonstandard header: '{lines[0]}'. "
            "Run clean_mol2_header() first to remove header lines."
        )

    # Get atom and bond counts from line index 2 (third line of file)
    counts = lines[2].split()
    natom = int(counts[0])
    nbond = int(counts[1])
    print(f"  Found {natom} atoms, {nbond} bonds in {mol2_path.name}")

    # Split file into pre-bond section and bond section
    bond_header_idx = None
    for i, line in enumerate(lines):
        if "@<TRIPOS>BOND" in line:
            bond_header_idx = i
            break

    if bond_header_idx is None:
        raise ValueError(f"No @<TRIPOS>BOND section found in {mol2_path}")

    pre_bond = lines[:bond_header_idx + 1]  # everything up to and including @<TRIPOS>BOND
    bond_lines_raw = lines[bond_header_idx + 1: bond_header_idx + 1 + nbond]

    # Parse bonds: normalize atom order so ai < aj
    bonds = []
    for line in bond_lines_raw:
        parts = line.split()
        # parts: [bond_id, atom_i, atom_j, bond_type]
        ai = int(parts[1])
        aj = int(parts[2])
        bond_type = parts[3]
        if aj < ai:
            ai, aj = aj, ai
        bonds.append((ai, aj, bond_type))

    # Sort by first atom, then second atom
    bonds.sort(key=lambda b: (b[0], b[1]))

    # Rebuild bond lines with renumbered bond IDs
    sorted_bond_lines = []
    for idx, (ai, aj, btype) in enumerate(bonds, start=1):
        sorted_bond_lines.append(f"{idx:6d}{ai:6d}{aj:6d} {btype}")

    # Write output
    output_text = "\n".join(pre_bond + sorted_bond_lines) + "\n"
    output_path.write_text(output_text)
    print(f"  Sorted {nbond} bonds in {output_path.name}")
