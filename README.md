# md-simulation

A script that automates the manual process of running a GROMACS MD simulation.

## Usage

```
md-simulation <sim_dir> [options]
```

`sim_dir` is the path to your simulation folder — the directory that already contains all input files (`REC.pdb`, `LIG.pdb`, `LIG.itp`, `.mdp` files, and the force field directory). Use `.` for the current directory.

### Examples

```
md-simulation simulation/           # run all steps
md-simulation .                     # use current directory
md-simulation simulation/ --step 3  # run only step 3
md-simulation simulation/ --from 5  # resume from step 5
```

### Flags

| Flag | Description |
|------|-------------|
| `--step N` | Run only step N and exits after finishing that step. |
| `--from N` | Runs from N onward. Useful for resuming a failed run. |
| `--no-visualize` | Skip all VMD visualization pauses. Useful for headless or automated runs. |
| `--windows` | Use the local VMD backend instead of Ray/XPRA. Required on Windows. |
| `--detach-step8` | Launch step 8 (production mdrun) in the background and return immediately. |
| `--detach` | Run the entire pipeline in the background. Feeds config values to all interactive prompts, skips VMD pauses, and launches step 8 as its own background process. Logs are written to `<sim_dir>/logs/`. |

Check progress after a detached run:

```
python -m research_work.status <sim_dir>
python -m research_work.status <sim_dir> --follow   # live refresh
```

---

## Configuration

Default parameters (box size, ion concentration, force field selections, etc.) are set in `config.py`:

```
src/research_work/config.py
```

Edit that file before running if you need to change any defaults. After editing, rebuild and reinstall the package so the changes take effect:

```
uv build
pip install dist/research_work-*.whl --force-reinstall
```

Or if you installed in editable mode (`pip install -e .`), changes take effect immediately without rebuilding.

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/masonbair/protein_gmx_automation
cd protein_gmx_automation
```

### 2. Build the package

```
uv build
```

### 3. Install

```
pip install -e .
```

### 4. Add the Scripts directory to PATH (Windows only)

Find where pip installed the scripts:

```
pip show research-work
```

Look for the `Location:` line, then append `\Scripts` to that path. Add it to your user PATH:

```powershell
[Environment]::SetEnvironmentVariable(
  "PATH",
  "$env:PATH;C:\Users\<you>\AppData\Roaming\Python\Python3xx\Scripts",
  "User"
)
```

Or via the GUI: **System Properties → Environment Variables → User variables → Path → Edit → New** and paste the Scripts path.

On Linux/macOS the scripts directory is added to PATH automatically.

### 5. Verify

```
md-simulation --help
```
