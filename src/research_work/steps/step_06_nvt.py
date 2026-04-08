"""
Step 6: NVT equilibration.

  - gmx grompp -f NVT.mdp -c EM.gro -r EM.gro -p topol.top -n index.ndx -o NVT.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm NVT
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_nvt():
    base_args = [
        "-f", MDP_FILES["nvt"],
        "-c", "EM.gro",
        "-r", "EM.gro",
        "-p", "topol.top",
        "-n", "index.ndx",
        "-o", "NVT.tpr",
    ]
    result = run_gmx("grompp", base_args, work_dir=SIM_DIR, check=False)
    if result.returncode == 0:
        return
    if "warning" in (result.stderr or "").lower():
        logger.warning("  grompp failed with warnings - retrying with -maxwarn %s.", MAXWARN)
        run_gmx("grompp", base_args, work_dir=SIM_DIR, maxwarn=MAXWARN)
    else:
        logger.error("grompp failed for reasons other than warnings.")
        raise SystemExit(1)


def mdrun_nvt():
    run_gmx("mdrun", ["-deffnm", "NVT"], work_dir=SIM_DIR)
    logger.info("  -> Produced: NVT.gro, NVT.edr, NVT.cpt, NVT.log, NVT.trr")


def run():
    logger.info("%s", "=" * 60)
    logger.info("STEP 6: NVT Equilibration")
    logger.info("%s", "=" * 60)

    logger.info("[6a] Assembling NVT.tpr with grompp...")
    grompp_nvt()

    logger.info("[6b] Running NVT equilibration (mdrun)...")
    mdrun_nvt()

    logger.info("Step 6 complete.")


if __name__ == "__main__":
    run()
