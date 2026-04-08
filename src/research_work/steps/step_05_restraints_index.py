"""
Step 5: Ligand position restraints and system index file.

Corresponds to tutorial lines 203-240:
  - gmx make_ndx -f LIG.gro -o index_LIG.ndx       (interactive)
        > 0 & ! a H*
        > q
  - gmx genrestr -f LIG.gro -n index_LIG.ndx -o posre_LIG.itp -fc 1000 1000 1000
        (interactive: pick the new non-H ligand group)
  - Edit topol.top to add the ligand POSRES include
  - gmx make_ndx -f EM.gro -o index.ndx            (interactive)
        > 1 | 13   (or whatever combo the user chooses)
        > q
"""

from research_work.config import SIM_DIR
from research_work.utils.gmx import run_gmx
from research_work.utils.file_edit import add_ligand_posres_include


def make_ligand_index():
    """
    gmx make_ndx -f LIG.gro -o index_LIG.ndx
    Interactive — user types selection (typically '0 & ! a H*' then 'q').
    """
    print("\n  Suggested selection: '0 & ! a H*'  then  'q'")
    print("  (creates a non-hydrogen ligand group used for restraints)")
    run_gmx(
        "make_ndx",
        ["-f", "LIG.gro", "-o", "index_LIG.ndx"],
        work_dir=SIM_DIR,
        interactive=True,
    )
    print("  -> Produced: index_LIG.ndx")


def genrestr_ligand():
    """
    gmx genrestr -f LIG.gro -n index_LIG.ndx -o posre_LIG.itp -fc 1000 1000 1000
    Interactive — user picks the non-H ligand group from the printed list.
    """
    print("\n  Pick the non-hydrogen ligand group you just created (often group 3).")
    run_gmx(
        "genrestr",
        [
            "-f", "LIG.gro",
            "-n", "index_LIG.ndx",
            "-o", "posre_LIG.itp",
            "-fc", "1000", "1000", "1000",
        ],
        work_dir=SIM_DIR,
        interactive=True,
    )
    print("  -> Produced: posre_LIG.itp")


def edit_topology_for_ligand_posres():
    """Append the ligand #ifdef POSRES include to topol.top (idempotent)."""
    add_ligand_posres_include(SIM_DIR / "topol.top", itp_name="posre_LIG.itp")


def make_system_index():
    """
    gmx make_ndx -f EM.gro -o index.ndx
    Interactive — user types the combo group they want (e.g. '1 | 13'),
    then 'q'. Group numbers depend on the system, so the user should read
    the printed list before choosing.
    """
    print("\n  Read the printed group list, then type the combination you want.")
    print("  Typical: 'Protein | LIG' (e.g. '1 | 13'), then 'q'.")
    run_gmx(
        "make_ndx",
        ["-f", "EM.gro", "-o", "index.ndx"],
        work_dir=SIM_DIR,
        interactive=True,
    )
    print("  -> Produced: index.ndx")


def run():
    print("\n" + "=" * 60)
    print("STEP 5: Ligand Restraints & System Index")
    print("=" * 60)

    print("\n[5a] Building ligand index file...")
    make_ligand_index()

    print("\n[5b] Generating ligand position restraints...")
    genrestr_ligand()

    print("\n[5c] Adding ligand POSRES include to topol.top...")
    edit_topology_for_ligand_posres()

    print("\n[5d] Building system index file (Protein + LIG combo)...")
    make_system_index()

    print("\nStep 5 complete.")


if __name__ == "__main__":
    run()
