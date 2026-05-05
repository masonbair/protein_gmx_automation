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
SIM_DIR = Path.home() / "protein_gmx_automation" / "simulation"

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
# Runtime default — use `--no-visualize` CLI flag to disable.
PAUSE_FOR_VISUALIZATION = True
# Runtime default — use `--windows` CLI flag to enable.
WINDOWS_MODE = False

# --- Detached Mode Defaults ---
# Values fed to interactive gmx prompts when running with `--detach`.
# Run the pipeline once interactively to discover the correct numbers for
# your system, then record them here.

# pdb2gmx (step 1): force-field number, then water-model number.
DETACH_PDB2GMX_FORCEFIELD = "1"
DETACH_PDB2GMX_WATER = "1"

# make_ndx on LIG.gro (step 5): lines sent to the interactive prompt to
# create the non-hydrogen ligand group and quit.
DETACH_MAKE_NDX_LIGAND = ["0 & ! a H*", "q"]

# genrestr on LIG.gro (step 5): group number of the non-H ligand group
# produced by the make_ndx step above.
DETACH_GENRESTR_LIGAND_GROUP = "3"

# make_ndx on EM.gro (step 5): lines sent to the interactive prompt to
# build the combined Protein+LIG group and quit.
DETACH_MAKE_NDX_SYSTEM = ["1 | 13", "q"]
# Ray Jobs API (dashboard) on xrpa-ray-container. Port 8265 is published
# by the container. Use the host gateway if the submitter runs in a
# sibling container (e.g. "http://host.docker.internal:8265" on Docker
# Desktop, or "http://172.17.0.1:8265" on a Linux default bridge).
RAY_JOBS_ADDRESS = "http://localhost:8265"
XPRA_DISPLAY = ":80"

# --- MDP Filenames (expected in SIM_DIR) ---
MDP_FILES = {
    "ions": "ions_NN.mdp",
    "em":   "em.mdp",
    "nvt":  "NVT.mdp",
    "npt":  "NPT.mdp",
    "md":   "MD_10M.mdp",
}
