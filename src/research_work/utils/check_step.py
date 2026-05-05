"""
Interactive warning review for gmx steps.

The research workflow starts every grompp-style call with no -maxwarn.
If GROMACS emits warnings, the command fails - at which point the user
needs to read the warnings, judge whether they are safe to ignore, and
either abort or rerun with -maxwarn <N>. This utility drives that
pause-and-decide loop so every step gets the same treatment.
"""

import logging
from pathlib import Path

from research_work.utils import console
from research_work.utils.gmx import run_gmx


logger = logging.getLogger(__name__)


def check_step(command: str, args: list[str], work_dir: Path | None = None,
               stdin_lines: list[str] | None = None,
               default_maxwarn: str | None = None,
               detach: bool = False) -> None:
    """
    Run a gmx command and gate on warnings.

    Runs once with no -maxwarn. If the command succeeds, returns. If it
    fails for a non-warning reason, aborts. If it fails because of
    warnings, the warnings are already in the log - prompt the user to
    either abort or supply a -maxwarn value and rerun.

    Parameters
    ----------
    command, args, work_dir, stdin_lines
        Forwarded to run_gmx.
    default_maxwarn
        Value used if the user presses Enter at the prompt. If None,
        pressing Enter aborts.
    detach
        If True, skip the interactive prompt entirely: auto-retry with
        default_maxwarn if it's set, otherwise abort.
    """
    result = run_gmx(
        command, args,
        work_dir=work_dir,
        stdin_lines=stdin_lines,
        check=False,
    )
    if result.returncode == 0:
        return

    stderr = result.stderr or ""
    if "warning" not in stderr.lower():
        logger.error("gmx %s failed for reasons other than warnings. See output above.", command)
        raise SystemExit(1)

    if detach:
        if default_maxwarn is None:
            logger.error("gmx %s emitted warnings; no default maxwarn set - aborting (detach mode).", command)
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


def _prompt_for_maxwarn(command: str, default_maxwarn: str | None) -> str:
    """
    Ask the user whether to abort or retry with a -maxwarn value.

    Returns the chosen maxwarn value. Raises SystemExit if the user
    chooses to abort or supplies an invalid value.
    """
    print()
    print("  ! gmx", command, "failed due to warning(s). Review the output above.")
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
