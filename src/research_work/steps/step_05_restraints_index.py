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

from research_work.config import (
    SIM_DIR,
    DETACH_MAKE_NDX_LIGAND,
    DETACH_GENRESTR_LIGAND_GROUP,
    DETACH_MAKE_NDX_SYSTEM,
)
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
    lig_itp = SIM_DIR / "LIG.itp"
    if not lig_itp.exists():
        return False
    text = lig_itp.read_text()
    return "POSRES_LIGAND" in text or "[ position_restraints ]" in text


def make_ligand_index(detach: bool = False):
    """
    gmx make_ndx -f LIG.gro -o index_LIG.ndx
    Interactive — user types selection (typically '0 & ! a H*' then 'q').
    In detach mode, uses DETACH_MAKE_NDX_LIGAND from config.
    """
    if detach:
        logger.info("  [detach] stdin=%s (from config)", DETACH_MAKE_NDX_LIGAND)
        run_gmx(
            "make_ndx",
            ["-f", "LIG.gro", "-o", "index_LIG.ndx"],
            stdin_lines=list(DETACH_MAKE_NDX_LIGAND),
            work_dir=SIM_DIR,
        )
    else:
        logger.info("  Suggested selection: '0 & ! a H*'  then  'q'")
        logger.info("  (creates a non-hydrogen ligand group used for restraints)")
        run_gmx(
            "make_ndx",
            ["-f", "LIG.gro", "-o", "index_LIG.ndx"],
            work_dir=SIM_DIR,
            interactive=True,
        )
    logger.info("  -> Produced: index_LIG.ndx")


def genrestr_ligand(detach: bool = False):
    """
    gmx genrestr -f LIG.gro -n index_LIG.ndx -o posre_LIG.itp -fc 1000 1000 1000
    Interactive — user picks the non-H ligand group from the printed list.
    In detach mode, uses DETACH_GENRESTR_LIGAND_GROUP from config.
    """
    if detach:
        logger.info(
            "  [detach] non-H ligand group=%s (from config)",
            DETACH_GENRESTR_LIGAND_GROUP,
        )
        run_gmx(
            "genrestr",
            [
                "-f", "LIG.gro",
                "-n", "index_LIG.ndx",
                "-o", "posre_LIG.itp",
                "-fc", "1000", "1000", "1000",
            ],
            stdin_lines=[DETACH_GENRESTR_LIGAND_GROUP],
            work_dir=SIM_DIR,
        )
    else:
        logger.info("  Pick the non-hydrogen ligand group you just created (often group 3).")
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
    logger.info("  -> Produced: posre_LIG.itp")


def edit_topology_for_ligand_posres():
    """
    Append the ligand #ifdef POSRES include to LIG.itp (idempotent).
    Must be LIG.itp, not topol.top — see add_ligand_posres_include() for why.
    """
    add_ligand_posres_include(SIM_DIR / "LIG.itp", itp_name="posre_LIG.itp")


def make_system_index(detach: bool = False):
    """
    gmx make_ndx -f EM.gro -o index.ndx
    Interactive — user types the combo group they want (e.g. '1 | 13'),
    then 'q'. Group numbers depend on the system, so the user should read
    the printed list before choosing.
    In detach mode, uses DETACH_MAKE_NDX_SYSTEM from config.
    """
    if detach:
        logger.info("  [detach] stdin=%s (from config)", DETACH_MAKE_NDX_SYSTEM)
        run_gmx(
            "make_ndx",
            ["-f", "EM.gro", "-o", "index.ndx"],
            stdin_lines=list(DETACH_MAKE_NDX_SYSTEM),
            work_dir=SIM_DIR,
        )
    else:
        logger.info("  Read the printed group list, then type the combination you want.")
        logger.info("  Typical: 'Protein | LIG' (e.g. '1 | 13'), then 'q'.")
        run_gmx(
            "make_ndx",
            ["-f", "EM.gro", "-o", "index.ndx"],
            work_dir=SIM_DIR,
            interactive=True,
        )
    logger.info("  -> Produced: index.ndx")


def run(detach: bool = False):
    logger.info("%s", "=" * 60)
    logger.info("STEP 5: Ligand Restraints & System Index")
    logger.info("%s", "=" * 60)

    if ligand_itp_has_inline_restraints():
        logger.info("  LIG.itp already contains inline position restraints (POSRES_LIGAND block).")
        logger.info("  Skipping ligand index, genrestr, and topol.top edit - they would")
        logger.info("  duplicate the existing restraints and break grompp.")
        logger.info("  IMPORTANT: make sure NVT.mdp / NPT.mdp activate the macro, e.g.:")
        logger.info("      define = -DPOSRES -DPOSRES_LIGAND")
    else:
        logger.info("[5a] Building ligand index file...")
        make_ligand_index(detach=detach)

        logger.info("[5b] Generating ligand position restraints...")
        genrestr_ligand(detach=detach)

        logger.info("[5c] Adding ligand POSRES include to LIG.itp...")
        edit_topology_for_ligand_posres()

    logger.info("[5d] Building system index file (Protein + LIG combo)...")
    make_system_index(detach=detach)

    logger.info("Step 5 complete.")


if __name__ == "__main__":
    run()
