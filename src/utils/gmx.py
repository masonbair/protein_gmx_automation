"""
Wrapper for running GROMACS (gmx) commands via subprocess.

Handles:
- Running gmx commands with arguments
- Piping interactive selections via stdin
- Interactive mode: show gmx prompts and let the user choose
- Logging command output
- Error checking
"""

import subprocess
import sys
from pathlib import Path


def run_gmx(command: str, args: list[str], stdin_lines: list[str] | None = None,
            work_dir: Path | None = None, maxwarn: str | None = None,
            interactive: bool = False) -> subprocess.CompletedProcess:
    """
    Run a gmx subcommand.

    Parameters
    ----------
    command : str
        The gmx subcommand (e.g. "pdb2gmx", "editconf", "solvate").
    args : list[str]
        Arguments to pass after `gmx <command>`.
    stdin_lines : list[str] or None
        Lines to feed to stdin for interactive prompts.
        Ignored if interactive=True.
    work_dir : Path or None
        Working directory for the command. Defaults to cwd.
    maxwarn : str or None
        If set, appends -maxwarn <value> to the args.
    interactive : bool
        If True, connects gmx directly to the terminal so the user
        can see prompts and type selections themselves.

    Returns
    -------
    subprocess.CompletedProcess
    """
    cmd = ["gmx", command] + args
    if maxwarn is not None:
        cmd.extend(["-maxwarn", maxwarn])

    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    if interactive:
        print("  (interactive — follow the prompts below)")
    elif stdin_lines:
        print(f"  stdin: {stdin_lines}")
    print(f"{'='*60}")

    if interactive:
        # Let gmx talk directly to the user's terminal
        result = subprocess.run(cmd, cwd=work_dir)
    else:
        stdin_text = None
        if stdin_lines:
            stdin_text = "\n".join(stdin_lines) + "\n"

        result = subprocess.run(
            cmd,
            input=stdin_text,
            cwd=work_dir,
            text=True,
            capture_output=True,
        )

        # gmx writes most output to stderr
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)

    if result.returncode != 0:
        print(f"\nERROR: gmx {command} exited with code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    return result


def run_shell(cmd: str, work_dir: Path | None = None) -> subprocess.CompletedProcess:
    """Run an arbitrary shell command (for non-gmx tools like vmd, xmgrace)."""
    print(f"\nRunning: {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=work_dir, text=True, capture_output=True,
    )
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(result.stderr)
    return result


def pause(message: str = "Press Enter to continue..."):
    """Pause execution and wait for user input."""
    print(f"\n>>> {message}")
    input()
