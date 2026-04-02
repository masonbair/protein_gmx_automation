"""
Configuration for the GROMACS MD simulation pipeline.
Edit paths and parameters here before running.
"""

from pathlib import Path

# --- Paths ---
# Root working directory where the simulation will run
WORK_DIR = Path.home() / "Desktop" / "programming" / "research_work"

# Where raw input files live (REC.pdb, LIG.mol2, SwissParam zip, etc.)
INPUT_DIR = WORK_DIR / "New MD general files"

# Where the simulation will be executed (created by the script)
SIM_DIR = WORK_DIR / "simulation"

# --- Input Filenames ---
RECEPTOR_PDB = "REC.pdb"
LIGAND_MOL2 = "LIG.mol2"
LIGAND_NAME = "LIG"  # Name used in topology files

# --- Force Field Selection (interactive prompt numbers) ---
FORCE_FIELD = "8"   # CHARMM27
WATER_MODEL = "1"   # TIP3P

# --- Box Parameters ---
BOX_DISTANCE = "1.0"    # nm from solute to box edge
BOX_TYPE = "triclinic"

# --- Ion Parameters ---
ION_CONCENTRATION = "0.1"  # mol/L
GENION_GROUP = "15"        # SOL group for ion replacement

# --- mdrun Parameters ---
MAXWARN = "2"

# --- Visualization ---
VMD_COMMAND = "vmd"
PAUSE_FOR_VISUALIZATION = True  # Set False to skip VMD pauses

# --- MDP files ---
MDP_FILES = {
    "ions": INPUT_DIR / "ions_NN.mdp",
    "em":   INPUT_DIR / "em.mdp",
    "nvt":  INPUT_DIR / "NVT.mdp",
    "npt":  INPUT_DIR / "NPT.mdp",
    "md":   INPUT_DIR / "MD_10M.mdp",
}
