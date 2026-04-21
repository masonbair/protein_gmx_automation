"""
Main entry point for the GROMACS MD simulation pipeline.

Usage:
    python run_md.py                 # Run all steps interactively
    python run_md.py --step 1        # Run only step 1
    python run_md.py --from 3        # Resume from step 3 onward
    python run_md.py --detach-step8  # Run step 8 mdrun in the background
    python run_md.py --detach        # Full detached run: feed config values
                                     # to every interactive prompt, skip
                                     # intermediate VMD pauses, and launch
                                     # step 8 in the background.
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


def _invoke(step_num: int, func, detach: bool, detach_step8: bool) -> None:
    """Call a step with the right kwargs. Step 8 accepts detach independently
    (so --detach-step8 works without --detach); every step accepts detach."""
    if step_num == 8:
        func(detach=(detach or detach_step8))
    else:
        func(detach=detach)


def main():
    parser = argparse.ArgumentParser(description="GROMACS MD Simulation Pipeline")
    parser.add_argument("--step", type=int, help="Run only this step")
    parser.add_argument("--from", dest="from_step", type=int, help="Start from this step")
    parser.add_argument(
        "--detach-step8",
        action="store_true",
        help="Launch step 8 production mdrun in the background and exit.",
    )
    parser.add_argument(
        "--detach",
        action="store_true",
        help=(
            "Run the entire pipeline without interactive prompts. Uses the "
            "DETACH_* values in config.py for steps 1 and 5, skips VMD "
            "pauses, auto-applies the default maxwarn on grompp warnings, "
            "and launches step 8 mdrun in the background. Check progress "
            "with: python -m research_work.status"
        ),
    )
    args = parser.parse_args()

    log_file = setup_logging(SIM_DIR / "logs")
    logger.info("Logging to file: %s", log_file)
    if args.detach:
        logger.info("Running in detached mode - no interactive prompts.")

    step_8_detached = False

    if args.step:
        if args.step not in STEPS:
            logger.error("Unknown step %s. Available: %s", args.step, list(STEPS.keys()))
            sys.exit(1)
        name, func = STEPS[args.step]
        logger.info(">>> Running step %s: %s", args.step, name)
        _invoke(args.step, func, args.detach, args.detach_step8)
        if args.step == 8 and (args.detach or args.detach_step8):
            step_8_detached = True
    else:
        start = args.from_step or 1
        for step_num in sorted(STEPS.keys()):
            if step_num < start:
                continue
            name, func = STEPS[step_num]
            logger.info(">>> Running step %s: %s", step_num, name)
            _invoke(step_num, func, args.detach, args.detach_step8)
            if step_num == 8 and (args.detach or args.detach_step8):
                step_8_detached = True

    logger.info("%s", "=" * 60)
    if step_8_detached:
        logger.info("Pipeline foreground portion complete.")
        logger.info("Step 8 is running in the background - it is NOT done yet.")
        logger.info("Check progress with: python -m research_work.status")
    else:
        logger.info("Pipeline complete.")
    logger.info("%s", "=" * 60)


if __name__ == "__main__":
    main()
