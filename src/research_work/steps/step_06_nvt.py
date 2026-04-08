"""
Step 6: NVT equilibration.

  - gmx grompp -f NVT.mdp -c EM.gro -r EM.gro -p topol.top -n index.ndx -o NVT.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm NVT
"""

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx


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
        print(f"\n  grompp failed with warnings — retrying with -maxwarn {MAXWARN}.")
        run_gmx("grompp", base_args, work_dir=SIM_DIR, maxwarn=MAXWARN)
    else:
        print("\nERROR: grompp failed for reasons other than warnings.")
        raise SystemExit(1)


def mdrun_nvt():
    run_gmx("mdrun", ["-deffnm", "NVT"], work_dir=SIM_DIR)
    print("  -> Produced: NVT.gro, NVT.edr, NVT.cpt, NVT.log, NVT.trr")


def run():
    print("\n" + "=" * 60)
    print("STEP 6: NVT Equilibration")
    print("=" * 60)

    print("\n[6a] Assembling NVT.tpr with grompp...")
    grompp_nvt()

    print("\n[6b] Running NVT equilibration (mdrun)...")
    mdrun_nvt()

    print("\nStep 6 complete.")


if __name__ == "__main__":
    run()
