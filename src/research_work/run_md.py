"""
Main entry point for the GROMACS MD simulation pipeline.

Usage:
    python run_md.py              # Run all steps from the beginning
    python run_md.py --step 1     # Run only step 1
    python run_md.py --from 3     # Resume from step 3 onward
"""

import argparse
import sys

from steps.step_01_prepare_ligand import run as step_01
from steps.step_02_edit_topology import run as step_02


STEPS = {
    1: ("Receptor Topology & Ligand Conversion", step_01),
    2: ("Edit Topology & ITP Files",             step_02),
    # 3: ("Solvate & Add Ions",                   step_03),
    # 4: ("Energy Minimization",                  step_04),
    # 5: ("Indexing & Restraints",                step_05),
    # 6: ("NVT Equilibration",                    step_06),
    # 7: ("NPT Equilibration",                    step_07),
    # 8: ("Production MD",                        step_08),
    # 9: ("Post-MD Analysis",                     step_09),
}


def main():
    parser = argparse.ArgumentParser(description="GROMACS MD Simulation Pipeline")
    parser.add_argument("--step", type=int, help="Run only this step")
    parser.add_argument("--from", dest="from_step", type=int, help="Start from this step")
    args = parser.parse_args()

    if args.step:
        if args.step not in STEPS:
            print(f"Unknown step {args.step}. Available: {list(STEPS.keys())}")
            sys.exit(1)
        name, func = STEPS[args.step]
        print(f"\n>>> Running step {args.step}: {name}")
        func()
    else:
        start = args.from_step or 1
        for step_num in sorted(STEPS.keys()):
            if step_num < start:
                continue
            name, func = STEPS[step_num]
            print(f"\n>>> Running step {step_num}: {name}")
            func()

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
