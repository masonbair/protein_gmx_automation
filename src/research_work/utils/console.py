"""
Print-based console output for the MD pipeline.

All functions write directly to stdout so output is visible regardless
of logging level.  The logger still captures everything to the pipeline
log file for debugging.  Works on both Linux terminals and Windows
PowerShell (pure ASCII, no ANSI codes).
"""

import sys
import time
from datetime import datetime

_W = 64


def step_header(n: int, name: str) -> float:
    """Print a step banner and return a monotonic start time."""
    ts = datetime.now().strftime("%H:%M:%S")
    print()
    print("=" * _W)
    print(f"  STEP {n}  --  {name}")
    print(f"  Started: {ts}")
    print("=" * _W)
    sys.stdout.flush()
    return time.monotonic()


def step_done(elapsed: float, note: str = "") -> None:
    """Print step completion with elapsed time."""
    m, s = divmod(int(elapsed), 60)
    dur = f"{m}m {s}s" if m else f"{s}s"
    suffix = f"  ({note})" if note else ""
    print(f"  Done  [{dur}]{suffix}")
    print("=" * _W)
    sys.stdout.flush()


def substep(label: str, description: str) -> None:
    """Print a substep label and description."""
    print(f"  [{label}]  {description}")
    sys.stdout.flush()


def cmd(cmdline: str) -> None:
    """Print the exact shell command being run."""
    print(f"        $ {cmdline}")
    sys.stdout.flush()


def hint(msg: str) -> None:
    """Print a usage hint or interactive instruction for the user."""
    print(f"        > {msg}")
    sys.stdout.flush()


def produced(files: str) -> None:
    """Print the output files produced."""
    print(f"        -> {files}")
    sys.stdout.flush()


def info(msg: str) -> None:
    """Print a plain informational line."""
    print(f"  {msg}")
    sys.stdout.flush()


def warn(msg: str) -> None:
    """Print a warning visible on the console."""
    print(f"  ! {msg}")
    sys.stdout.flush()
