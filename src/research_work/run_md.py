"""
Main entry point for the GROMACS MD simulation pipeline.

Usage:
    python run_md.py              # Run all steps from the beginning
    python run_md.py --step 1     # Run only step 1
    python run_md.py --from 3     # Resume from step 3 onward
"""

import argparse
import logging
import sys

from research_work.config import SIM_DIR
from research_work.steps.step_01_prepare_ligand import run as step_01
from research_work.steps.step_02_edit_topology import run as step_02
from research_work.steps.step_03_add_ions import run as step_03
from research_work.steps.step_04_energy_min import run as step_04
from research_work.steps.step_05_restraints_index import run as step_05
from research_work.steps.step_06_nvt import run as step_06
from research_work.steps.step_07_npt import run as step_07
from research_work.steps.step_08_production_md import run as step_08
from research_work.utils.logging_setup import setup_logging


STEPS = {
    1: ("Receptor Topology & Ligand Conversion", step_01),
    2: ("Edit Topology & ITP Files",             step_02),
    3: ("Solvate & Add Ions",                    step_03),
    4: ("Energy Minimization",                   step_04),
    5: ("Restraints & System Index",             step_05),
    6: ("NVT Equilibration",                     step_06),
    7: ("NPT Equilibration",                     step_07),
    8: ("Production MD",                         step_08),
    # 9: ("Post-MD Analysis",                     step_09),
}


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="GROMACS MD Simulation Pipeline")
    parser.add_argument("--step", type=int, help="Run only this step")
    parser.add_argument("--from", dest="from_step", type=int, help="Start from this step")
    args = parser.parse_args()

    log_file = setup_logging(SIM_DIR / "logs")
    logger.info("Logging to file: %s", log_file)

    if args.step:
        if args.step not in STEPS:
            logger.error("Unknown step %s. Available: %s", args.step, list(STEPS.keys()))
            sys.exit(1)
        name, func = STEPS[args.step]
        logger.info(">>> Running step %s: %s", args.step, name)
        func()
    else:
        start = args.from_step or 1
        for step_num in sorted(STEPS.keys()):
            if step_num < start:
                continue
            name, func = STEPS[step_num]
            logger.info(">>> Running step %s: %s", step_num, name)
            func()

    logger.info("%s", "=" * 60)
    logger.info("Pipeline complete.")
    logger.info("%s", "=" * 60)


if __name__ == "__main__":
    main()
