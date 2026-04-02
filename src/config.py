"""
Configuration for the GROMACS MD simulation pipeline.
Edit paths and parameters here before running.

Prerequisites: The user has already prepared the working folder with:
  REC.pdb, LIG.pdb, LIG.itp, lig.itp, all .mdp files,
  and the force field directory (e.g. charmm36-jul2022.ff/).
"""

from pathlib import Path

# --- Paths ---
# The simulation working folder - should already contain all input files.
# Change this to wherever your prepared GROMACS folder is.
SIM_DIR = Path.home() / "Desktop" / "programming" / "research_work" / "simulation"

# --- Input Filenames ---
RECEPTOR_PDB = "REC.pdb"
LIGAND_NAME = "LIG"  # Name used in topology files

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

# --- MDP Filenames (expected in SIM_DIR) ---
MDP_FILES = {
    "ions": "ions_NN.mdp",
    "em":   "em.mdp",
    "nvt":  "NVT.mdp",
    "npt":  "NPT.mdp",
    "md":   "MD_10M.mdp",
}
