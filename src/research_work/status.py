"""
Pipeline status inspector.

Shows the current state of a (possibly detached) MD run. Meant to be
invoked as:

    python -m research_work.status
    python -m research_work.status -n 40            # more tail lines
    python -m research_work.status --follow         # refresh in place

It looks at SIM_DIR/logs and reports:
  * whether the detached step 8 mdrun wrapper is still alive (PID check),
  * a tail of the most recent pipeline_*.log,
  * a tail of step8_mdrun.out (the live mdrun output).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from research_work.config import SIM_DIR


def pid_alive(pid: int) -> bool:
    """Return True if a process with this PID is running.

    Uses kill(pid, 0), which on Linux raises ProcessLookupError when the
    PID is gone and PermissionError when it exists but is owned by
    someone else (still alive for our purposes).
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_pid(pid_path: Path) -> int | None:
    try:
        return int(pid_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _latest_pipeline_log(logs_dir: Path) -> Path | None:
    candidates = sorted(logs_dir.glob("pipeline_*.log"))
    return candidates[-1] if candidates else None


def _tail(path: Path, n: int) -> str:
    if not path.exists():
        return f"[not found: {path}]\n"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as exc:
        return f"[error reading {path}: {exc}]\n"
    return "".join(lines[-n:]) if lines else "[empty]\n"


def _print_section(title: str) -> None:
    print("-" * 60)
    print(title)
    print("-" * 60)


def show_status(n_lines: int, out=sys.stdout) -> None:
    logs_dir = SIM_DIR / "logs"

    print("=" * 60, file=out)
    print(f"MD pipeline status  (SIM_DIR = {SIM_DIR})", file=out)
    print(f"Checked at:         {time.strftime('%Y-%m-%d %H:%M:%S')}", file=out)
    print("=" * 60, file=out)

    if not logs_dir.exists():
        print(f"No logs directory found at {logs_dir}.", file=out)
        return

    pid_path = logs_dir / "step8_mdrun.pid"
    pid = _read_pid(pid_path)
    if pid is None:
        print("Detached step 8: no PID file (step 8 was not launched detached).", file=out)
    else:
        state = "RUNNING" if pid_alive(pid) else "EXITED"
        print(f"Detached step 8: PID {pid} - {state}", file=out)

    latest = _latest_pipeline_log(logs_dir)
    print(file=out)
    if latest is None:
        print("No pipeline_*.log files found in logs dir.", file=out)
    else:
        _print_section(f"Latest pipeline log: {latest.name}")
        print(_tail(latest, n_lines), end="", file=out)

    out_path = logs_dir / "step8_mdrun.out"
    err_path = logs_dir / "step8_mdrun.err"
    if out_path.exists():
        print(file=out)
        _print_section(f"step8 mdrun stdout: {out_path.name}")
        print(_tail(out_path, n_lines), end="", file=out)
    if err_path.exists() and err_path.stat().st_size > 0:
        print(file=out)
        _print_section(f"step8 mdrun stderr: {err_path.name}")
        print(_tail(err_path, n_lines), end="", file=out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show the current status of the MD pipeline.",
    )
    parser.add_argument(
        "-n", "--lines", type=int, default=20,
        help="Number of tail lines to show per section (default: 20).",
    )
    parser.add_argument(
        "-f", "--follow", action="store_true",
        help="Re-print the status on an interval (Ctrl-C to stop).",
    )
    parser.add_argument(
        "--interval", type=float, default=5.0,
        help="Refresh interval in seconds for --follow (default: 5.0).",
    )
    args = parser.parse_args()

    if not args.follow:
        show_status(args.lines)
        return

    try:
        while True:
            # Clear the screen between refreshes so the status stays in place.
            os.system("clear" if os.name == "posix" else "cls")
            show_status(args.lines)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
