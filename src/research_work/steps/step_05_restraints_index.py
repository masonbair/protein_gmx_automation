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

import logging
import time

from research_work import config
from research_work.config import (
    DETACH_MAKE_NDX_LIGAND,
    DETACH_GENRESTR_LIGAND_GROUP,
    DETACH_MAKE_NDX_SYSTEM,
)
from research_work.utils import console
from research_work.utils.gmx import run_gmx
from research_work.utils.file_edit import add_ligand_posres_include


logger = logging.getLogger(__name__)


def ligand_itp_has_inline_restraints() -> bool:
    """
    Detect whether LIG.itp already contains an inline position-restraints
    block (typically gated on the POSRES_LIGAND macro). If so, the genrestr
    + topology-edit substeps are not just unnecessary, they're harmful:
    appending a #include for posre_LIG.itp at the end of topol.top puts the
    restraints outside any [moleculetype] and grompp errors with
    "Atom index ... out of bounds".
    """
    lig_itp = config.SIM_DIR / "LIG.itp"
    if not lig_itp.exists():
        return False
    text = lig_itp.read_text()
    return "POSRES_LIGAND" in text or "[ position_restraints ]" in text


def make_ligand_index(detach: bool = False):
    if detach:
        console.info(f"[detach] stdin={DETACH_MAKE_NDX_LIGAND} (from config)")
        run_gmx(
            "make_ndx",
            ["-f", "LIG.gro", "-o", "index_LIG.ndx"],
            stdin_lines=list(DETACH_MAKE_NDX_LIGAND),
            work_dir=config.SIM_DIR,
        )
    else:
        console.hint("Type '0 & ! a H*' then 'q' to create the non-hydrogen ligand group.")
        run_gmx(
            "make_ndx",
            ["-f", "LIG.gro", "-o", "index_LIG.ndx"],
            work_dir=config.SIM_DIR,
            interactive=True,
        )
    console.produced("index_LIG.ndx")


def genrestr_ligand(detach: bool = False):
    if detach:
        console.info(f"[detach] non-H ligand group={DETACH_GENRESTR_LIGAND_GROUP} (from config)")
        run_gmx(
            "genrestr",
            ["-f", "LIG.gro", "-n", "index_LIG.ndx", "-o", "posre_LIG.itp", "-fc", "1000", "1000", "1000"],
            stdin_lines=[DETACH_GENRESTR_LIGAND_GROUP],
            work_dir=config.SIM_DIR,
        )
    else:
        console.hint("Pick the non-hydrogen ligand group you just created (often group 3).")
        run_gmx(
            "genrestr",
            ["-f", "LIG.gro", "-n", "index_LIG.ndx", "-o", "posre_LIG.itp", "-fc", "1000", "1000", "1000"],
            work_dir=config.SIM_DIR,
            interactive=True,
        )
    console.produced("posre_LIG.itp")


def edit_topology_for_ligand_posres():
    add_ligand_posres_include(config.SIM_DIR / "LIG.itp", itp_name="posre_LIG.itp")


def make_system_index(detach: bool = False):
    if detach:
        console.info(f"[detach] stdin={DETACH_MAKE_NDX_SYSTEM} (from config)")
        run_gmx(
            "make_ndx",
            ["-f", "EM.gro", "-o", "index.ndx"],
            stdin_lines=list(DETACH_MAKE_NDX_SYSTEM),
            work_dir=config.SIM_DIR,
        )
    else:
        console.hint("Read the group list, type your combination (e.g. '1 | 13'), then 'q'.")
        run_gmx(
            "make_ndx",
            ["-f", "EM.gro", "-o", "index.ndx"],
            work_dir=config.SIM_DIR,
            interactive=True,
        )
    console.produced("index.ndx")


def run(detach: bool = False):
    start = console.step_header(5, "Ligand Restraints & System Index")

    if ligand_itp_has_inline_restraints():
        console.info("LIG.itp already contains inline position restraints (POSRES_LIGAND block).")
        console.info("Skipping ligand index, genrestr, and topology edit.")
        console.info("Ensure NVT.mdp / NPT.mdp define: -DPOSRES -DPOSRES_LIGAND")
    else:
        console.substep("5a", "Building ligand index file (gmx make_ndx)")
        make_ligand_index(detach=detach)

        console.substep("5b", "Generating ligand position restraints (gmx genrestr)")
        genrestr_ligand(detach=detach)

        console.substep("5c", "Adding POSRES include to LIG.itp")
        edit_topology_for_ligand_posres()

    console.substep("5d", "Building system index file (gmx make_ndx)")
    make_system_index(detach=detach)

    console.step_done(time.monotonic() - start)


if __name__ == "__main__":
    run()
