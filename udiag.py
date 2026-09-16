import os
import subprocess
import argparse
import sys

from mode_manager import prepare_modes
from structure import ModeDict, Operation, create_operation

from terminal import present_terminal, terminal_title

env_with_colors = os.environ.copy()
env_with_colors["SYSTEMD_COLORS"] = "1"

def prepare_args(modes: list[ModeDict]) -> list[str]:
    """Prepares a list of arguments for each specific mode."""
    args_list: list[str] = []
    for mode in modes:
        args_list.append(mode["name"])

    return args_list

def build_parser(correct_modes: list[ModeDict]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Udiag - Diagnostic system with JSON"
    )

    mode_names = prepare_args(correct_modes)

    # Errors
    parser.add_argument(
        "-e",
        "--errors",
        dest="mode_errors",
        action="store_true",
        help="Check mode errors"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # Run
    run_parser = subparsers.add_parser(
        "run",
        help="Run diagnostic mode"
    )

    run_parser.add_argument(
        "mode",
        choices=mode_names
    )

    # Show
    show_parser = subparsers.add_parser(
        "show",
        help="Show mode details"
    )

    show_parser.add_argument(
        "mode",
        choices=mode_names
    )

    return parser

def warning(errors: list[str]) -> None:
    if errors:
        print()
        print(f"{len(errors)} : Modes are not available")
        print("For details, run udiag.py -e, --errors" + "\n")

def warning_details(errors: list[str]) -> None:
    if errors:
        print(f"{len(errors)} : Modes are not available")
        print("Details:" + "\n")

        for i, error in enumerate(errors, start=1):
            print(f"{i}. {error}" + "\n")

        return

    print("No errors.")

def execute(operation: Operation) -> None:
    result = subprocess.run([operation.program, *operation.args],
                            capture_output=True,
                            text=True,
                            env=env_with_colors)

    operation.stdout = result.stdout
    operation.stderr = result.stderr
    operation.returncode = result.returncode

def main(args, correct_modes: list[ModeDict], errors: list[str]) -> None:
    # Errors
    if args.mode_errors:
        warning_details(errors)
        return
    
    # Run
    if args.command == "run":
        for mode in correct_modes:
            if args.mode == mode["name"]:
                warning(errors)
                print()

                terminal_title(mode)

                for i, instruction in enumerate(
                    mode["operations"],
                    start=1
                ):
                    operation = create_operation(instruction)
                    execute(operation)
                    present_terminal(i, instruction, operation)

                print("# End.")

    # Show
    if args.command == "show":
        for mode in correct_modes:
            if args.mode == mode["name"]:
                warning(errors)
                print()

                print(f"Mode: {mode["name"]}")
                print(f"Description: {mode["description"] + "\n"}")

                for i, instruction in enumerate(mode['operations'], start=1):
                    print(f"{instruction['title']}:")
                    print(f"	Program: {instruction['program']}")
                    print(f"	Arguments: {instruction['args']}\n")

                print("# End.")

if __name__ == "__main__":
    correct_modes, errors = prepare_modes()

    parser = build_parser(correct_modes)
    args = parser.parse_args()

    if not args.mode_errors and args.command is None:
        parser.print_help()
        sys.exit(0)

    main(args, correct_modes, errors)
