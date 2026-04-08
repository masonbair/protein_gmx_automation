"""
Step 7: NPT equilibration.

  - gmx grompp -f NPT.mdp -c NVT.gro -r NVT.gro -p topol.top -n index.ndx -o NPT.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm NPT
"""

import logging

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def grompp_npt():
    base_args = [
        "-f", MDP_FILES["npt"],
        "-c", "NVT.gro",
        "-r", "NVT.gro",
        "-p", "topol.top",
        "-n", "index.ndx",
        "-o", "NPT.tpr",
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


def mdrun_npt():
    run_gmx("mdrun", ["-deffnm", "NPT"], work_dir=SIM_DIR)
    logger.info("  -> Produced: NPT.gro, NPT.edr, NPT.cpt, NPT.log, NPT.trr")


def run():
    logger.info("%s", "=" * 60)
    logger.info("STEP 7: NPT Equilibration")
    logger.info("%s", "=" * 60)

    logger.info("[7a] Assembling NPT.tpr with grompp...")
    grompp_npt()

    logger.info("[7b] Running NPT equilibration (mdrun)...")
    mdrun_npt()

    logger.info("Step 7 complete.")


if __name__ == "__main__":
    run()
