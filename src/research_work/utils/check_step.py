"""
Interactive warning/note review for gmx steps.

The research workflow starts every grompp-style call with no -maxwarn.
If GROMACS emits warnings the command fails — the user reads the output,
judges whether the warnings are safe, and either aborts or reruns with
-maxwarn <N>.

GROMACS also emits NOTEs on otherwise-successful runs.  Notes never
cause a non-zero exit, but they can indicate important issues (e.g. bad
MDP settings).  This utility pauses on notes too so the user can review
them before the pipeline continues.
"""

import logging
from pathlib import Path

from research_work.utils import console
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def _has_warnings(stderr: str) -> bool:
    return "warning" in stderr.lower()


def _has_notes(stderr: str) -> bool:
    # GROMACS always writes "NOTE" in uppercase; checking case-sensitively
    # avoids false positives from the word "note" in other contexts.
    return "NOTE" in stderr


def _print_gmx_output(stderr: str) -> None:
    if stderr.strip():
        print()
        print(stderr.strip())
        print()


def check_step(command: str, args: list[str], work_dir: Path | None = None,
               stdin_lines: list[str] | None = None,
               default_maxwarn: str | None = None,
               detach: bool = False) -> None:
    """
    Run a gmx command and gate on warnings and notes.

    On success with no notes: returns immediately.
    On success with NOTEs: prints the output and prompts the user to
        continue or abort (notes never require -maxwarn).
    On failure due to warnings/notes: prints the output and prompts for
        a -maxwarn value, then retries.
    On failure for other reasons: prints the output and aborts.

    Parameters
    ----------
    command, args, work_dir, stdin_lines
        Forwarded to run_gmx.
    default_maxwarn
        Value used if the user presses Enter at the warning prompt. If
        None, pressing Enter aborts.
    detach
        If True, skip interactive prompts: auto-continue past notes and
        auto-retry with default_maxwarn on warnings.
    """
    result = run_gmx(
        command, args,
        work_dir=work_dir,
        stdin_lines=stdin_lines,
        check=False,
    )

    stderr = result.stderr or ""

    if result.returncode == 0:
        if _has_notes(stderr):
            _print_gmx_output(stderr)
            if detach:
                console.warn(f"gmx {command} printed note(s) -- continuing in detach mode.")
                logger.warning("gmx %s printed note(s); continuing (detach).", command)
            else:
                _prompt_for_note(command)
        return

    # Non-zero exit: decide whether it's warning/note related or a hard error.
    if not _has_warnings(stderr) and not _has_notes(stderr):
        _print_gmx_output(stderr)
        logger.error("gmx %s failed for reasons other than warnings/notes.", command)
        raise SystemExit(1)

    _print_gmx_output(stderr)

    if detach:
        if default_maxwarn is None:
            logger.error(
                "gmx %s emitted warnings; no default maxwarn set - aborting (detach mode).",
                command,
            )
            raise SystemExit(1)
        console.warn(f"gmx {command} emitted warnings; auto-retrying with -maxwarn {default_maxwarn}.")
        logger.warning("gmx %s emitted warnings; auto-retrying with -maxwarn %s.", command, default_maxwarn)
        maxwarn = default_maxwarn
    else:
        maxwarn = _prompt_for_maxwarn(command, default_maxwarn)

    console.warn(f"Retrying gmx {command} with -maxwarn {maxwarn} ...")
    logger.warning("Retrying gmx %s with -maxwarn %s ...", command, maxwarn)
    run_gmx(
        command, args,
        work_dir=work_dir,
        stdin_lines=stdin_lines,
        maxwarn=maxwarn,
    )


def _prompt_for_note(command: str) -> None:
    """Pause after a NOTE so the user can decide whether to continue."""
    print(f"  > gmx {command} printed note(s) -- review above.")
    print("    Press Enter to continue or 'q' to abort.")
    try:
        response = input("  continue [Enter/q] > ").strip()
    except EOFError:
        response = ""
    if response.lower() in ("q", "quit", "abort", "n", "no"):
        logger.error("User chose to abort after reviewing note.")
        raise SystemExit(1)


def _prompt_for_maxwarn(command: str, default_maxwarn: str | None) -> str:
    """
    Ask the user whether to abort or retry with a -maxwarn value.

    Returns the chosen maxwarn value. Raises SystemExit if the user
    chooses to abort or supplies an invalid value.
    """
    print()
    print(f"  ! gmx {command} emitted warning(s) -- see output above.")
    if default_maxwarn is not None:
        print(f"    Press Enter to retry with -maxwarn {default_maxwarn},")
        print("    or enter a different number, or type 'q' to abort.")
        prompt = f"  maxwarn [{default_maxwarn}] > "
    else:
        print("    Enter a -maxwarn value to retry, or press Enter / type 'q' to abort.")
        prompt = "  maxwarn > "

    try:
        response = input(prompt).strip()
    except EOFError:
        response = ""

    if response.lower() in ("", "q", "quit", "stop", "abort", "n", "no"):
        if response == "" and default_maxwarn is not None:
            return default_maxwarn
        logger.error("User chose to abort.")
        raise SystemExit(1)

    if not response.isdigit():
        logger.error("Invalid maxwarn value '%s' - aborting.", response)
        raise SystemExit(1)

    return response
