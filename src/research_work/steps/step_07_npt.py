"""
Step 7: NPT equilibration.

  - gmx grompp -f NPT.mdp -c NVT.gro -r NVT.gro -p topol.top -n index.ndx -o NPT.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm NPT
"""

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx


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
        print(f"\n  grompp failed with warnings — retrying with -maxwarn {MAXWARN}.")
        run_gmx("grompp", base_args, work_dir=SIM_DIR, maxwarn=MAXWARN)
    else:
        print("\nERROR: grompp failed for reasons other than warnings.")
        raise SystemExit(1)


def mdrun_npt():
    run_gmx("mdrun", ["-deffnm", "NPT"], work_dir=SIM_DIR)
    print("  -> Produced: NPT.gro, NPT.edr, NPT.cpt, NPT.log, NPT.trr")


def run():
    print("\n" + "=" * 60)
    print("STEP 7: NPT Equilibration")
    print("=" * 60)

    print("\n[7a] Assembling NPT.tpr with grompp...")
    grompp_npt()

    print("\n[7b] Running NPT equilibration (mdrun)...")
    mdrun_npt()

    print("\nStep 7 complete.")


if __name__ == "__main__":
    run()
