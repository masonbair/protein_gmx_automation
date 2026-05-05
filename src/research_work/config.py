"""
Configuration for the GROMACS MD simulation pipeline.
Edit parameters here before running. SIM_DIR is set at runtime via the
mandatory `sim_dir` CLI argument — do not set it here.
"""

from __future__ import annotations
from pathlib import Path

# --- Runtime state (set by CLI, do not edit) ---
SIM_DIR: Path | None = None

# --- Input Filenames ---
RECEPTOR_PDB = "REC.pdb"
LIGAND_NAME = "LIG"

# --- Box Parameters ---
BOX_DISTANCE = "1.0"    # nm from solute to box edge
BOX_TYPE = "triclinic"

# --- Ion Parameters ---
ION_CONCENTRATION = "0.1"  # mol/L
GENION_GROUP = "15"         # SOL group for ion replacement

# --- mdrun Parameters ---
MAXWARN = "2"

# --- Visualization ---
VMD_COMMAND = "vmd"
PAUSE_FOR_VISUALIZATION = True   # disable with --no-visualize
WINDOWS_MODE = False             # enable with --windows

# --- Detached Mode Defaults ---
# Values fed to interactive gmx prompts when running with `--detach`.
# Run the pipeline once interactively to discover the correct numbers,
# then record them here.

# pdb2gmx (step 1): force-field number, then water-model number.
DETACH_PDB2GMX_FORCEFIELD = "1"
DETACH_PDB2GMX_WATER = "1"

# make_ndx on LIG.gro (step 5): build non-hydrogen ligand group and quit.
DETACH_MAKE_NDX_LIGAND = ["0 & ! a H*", "q"]

# genrestr on LIG.gro (step 5): group number from the make_ndx step above.
DETACH_GENRESTR_LIGAND_GROUP = "3"

# make_ndx on EM.gro (step 5): build combined Protein+LIG group and quit.
DETACH_MAKE_NDX_SYSTEM = ["1 | 13", "q"]

# --- Ray / XPRA (Linux visualization backend) ---
# Port 8265 is published by xrpa-ray-container. Use the host gateway
# from a sibling container (e.g. "http://172.17.0.1:8265" on Linux).
RAY_JOBS_ADDRESS = "http://localhost:8265"
XPRA_DISPLAY = ":80"

# --- MDP Filenames (must exist inside sim_dir) ---
MDP_FILES = {
    "ions": "ions_NN.mdp",
    "em":   "em.mdp",
    "nvt":  "NVT.mdp",
    "npt":  "NPT.mdp",
    "md":   "MD_10M.mdp",
}
