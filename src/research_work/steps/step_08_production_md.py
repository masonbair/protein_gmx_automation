"""
Step 8: Production MD run.

  - gmx grompp -f MD.mdp -c NPT.gro -t NPT.cpt -p topol.top -n index.ndx -o MD.tpr
      (auto-retry with -maxwarn N if warnings cause failure)
  - gmx mdrun -deffnm MD -v

To resume an interrupted production run, use:
    gmx mdrun -s MD.tpr -cpi MD.cpt -deffnm MD -append -v
"""

from research_work.config import SIM_DIR, MDP_FILES, MAXWARN
from research_work.utils.gmx import run_gmx
from research_work.utils.visualize import visualize


def grompp_md():
    base_args = [
        "-f", MDP_FILES["md"],
        "-c", "NPT.gro",
        "-t", "NPT.cpt",
        "-p", "topol.top",
        "-n", "index.ndx",
        "-o", "MD.tpr",
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


def mdrun_md():
    """
    Production mdrun. If a checkpoint exists from a prior interrupted run,
    GROMACS users typically resume manually with:
        gmx mdrun -s MD.tpr -cpi MD.cpt -deffnm MD -append -v
    """
    run_gmx("mdrun", ["-deffnm", "MD", "-v"], work_dir=SIM_DIR)
    print("  -> Produced: MD.gro, MD.xtc, MD.edr, MD.cpt, MD.log")


def run():
    print("\n" + "=" * 60)
    print("STEP 8: Production MD")
    print("=" * 60)

    print("\n[8a] Assembling MD.tpr with grompp...")
    grompp_md()

    print("\n[8b] Running production MD (this may take a while)...")
    mdrun_md()

    print("\nStep 8 complete — production run finished.")
    print("\nLaunching final visualization of the production trajectory...")
    visualize(SIM_DIR / "MD.gro", label="final production MD")


if __name__ == "__main__":
    run()
