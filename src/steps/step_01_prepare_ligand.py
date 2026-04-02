"""
Step 1: Prepare the ligand (LIG.mol2).

This step handles:
1. [MANUAL] User prepares LIG.mol2 in Chimera (open best pose, delete protein,
   add hydrogens, save as LIG.mol2).
2. Clean the mol2 header so @<TRIPOS>MOLECULE is line 1.
3. Set the molecule name to "LIG".
4. Sort the @<TRIPOS>BOND section for GROMACS compatibility.
5. [MANUAL] User uploads LIG.mol2 to SwissParam and downloads the zip.
6. Extract the SwissParam zip into the simulation directory.
"""

import shutil
import zipfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import INPUT_DIR, SIM_DIR, LIGAND_MOL2, LIGAND_NAME
from utils.file_edit import clean_mol2_header, sort_mol2_bonds
from utils.gmx import pause


def run():
    print("\n" + "=" * 60)
    print("STEP 1: Prepare Ligand")
    print("=" * 60)

    # --- 1. Manual: Chimera preparation ---
    print(
        "\n[MANUAL STEP] Prepare LIG.mol2 in Chimera:\n"
        "  1. Open the best-pose ligand + receptor .pdb file.\n"
        "  2. Delete the protein chain.\n"
        "  3. Add hydrogens to the remaining ligand.\n"
        f"  4. Save as '{LIGAND_MOL2}' in:\n"
        f"     {INPUT_DIR}\n"
    )
    pause("Press Enter once LIG.mol2 is ready in the input directory...")

    # --- 2. Verify file exists ---
    mol2_src = INPUT_DIR / LIGAND_MOL2
    if not mol2_src.exists():
        print(f"ERROR: {mol2_src} not found. Please create it and re-run.")
        sys.exit(1)

    # --- 3. Set up simulation directory ---
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    mol2_dst = SIM_DIR / LIGAND_MOL2
    shutil.copy2(mol2_src, mol2_dst)
    print(f"Copied {LIGAND_MOL2} to {SIM_DIR}")

    # --- 4. Clean header and set molecule name ---
    print("\nCleaning mol2 file...")
    clean_mol2_header(mol2_dst, molecule_name=LIGAND_NAME)

    # --- 5. Sort bond section ---
    print("Sorting bond section...")
    sort_mol2_bonds(mol2_dst)

    # --- 6. Manual: SwissParam ---
    print(
        "\n[MANUAL STEP] SwissParam:\n"
        "  1. Go to http://www.swissparam.ch/\n"
        f"  2. Upload: {mol2_dst}\n"
        "  3. Download the resulting .zip file.\n"
        f"  4. Save the .zip into: {INPUT_DIR}\n"
    )
    pause("Press Enter once the SwissParam .zip is downloaded...")

    # --- 7. Find and extract the SwissParam zip ---
    zip_files = list(INPUT_DIR.glob("*.zip"))
    # Filter out known non-SwissParam zips
    zip_files = [z for z in zip_files if "general" not in z.stem.lower()]

    if not zip_files:
        # Also check SIM_DIR in case they put it there
        zip_files = list(SIM_DIR.glob("*.zip"))

    if not zip_files:
        print(
            "WARNING: No .zip file found. You can manually extract the SwissParam\n"
            f"  zip contents into {SIM_DIR} and continue."
        )
        pause("Press Enter to continue anyway...")
    else:
        # Use the most recently modified zip
        swissparam_zip = max(zip_files, key=lambda p: p.stat().st_mtime)
        print(f"\nExtracting {swissparam_zip.name} into {SIM_DIR}...")
        with zipfile.ZipFile(swissparam_zip, "r") as zf:
            zf.extractall(SIM_DIR)
        print("  Done.")

    # --- 8. Verify key output files ---
    expected_files = ["LIG.itp", "LIG.pdb"]
    missing = [f for f in expected_files if not (SIM_DIR / f).exists()]
    if missing:
        print(f"\nWARNING: Expected files not found in {SIM_DIR}: {missing}")
        print("  These should come from the SwissParam zip. Check extraction.")
    else:
        print(f"\nStep 1 complete. Ligand files ready in {SIM_DIR}:")
        for f in sorted(SIM_DIR.iterdir()):
            print(f"  {f.name}")


if __name__ == "__main__":
    run()
