import os
import subprocess
import argparse
import sys

from mode_manager import prepare_modes, find_mode_files
from structure import ModeDict, Operation, create_operation

from terminal import present_terminal, terminal_title

env_with_colors = os.environ.copy()
env_with_colors["SYSTEMD_COLORS"] = "1"

def get_mode_names(modes: list[ModeDict]) -> list[str]:
    """Prepares a list of arguments for each specific mode."""
    args_list: list[str] = []
    for mode_files in modes:
        args_list.append(mode_files["name"])

    return args_list

def build_parser(valid_modes: list[ModeDict]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Udiag - Diagnostic system with JSON"
    )

    mode_names = get_mode_names(valid_modes)

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

def print_mode_warning(errors: list[str]) -> None:
    if errors:
        print()
        print(f"{len(errors)} : Modes are not available")
        print("For details, run udiag.py -e, --errors" + "\n")

def print_mode_errors(errors: list[str]) -> None:
    if errors:
        print(f"{len(errors)} : Modes are not available")
        print("Details:" + "\n")

        for i, error in enumerate(errors, start=1):
            print(f"{i}. {error}" + "\n")

        return

    print("No errors.")

def execute_operation(operation: Operation) -> None:
    result = subprocess.run([operation.program, *operation.args],
                            capture_output=True,
                            text=True,
                            env=env_with_colors)

    operation.stdout = result.stdout
    operation.stderr = result.stderr
    operation.returncode = result.returncode

def main(args, valid_modes: list[ModeDict], errors: list[str]) -> None:
    # Errors
    if args.mode_errors:
        print_mode_errors(errors)
        return
    
    # Run
    if args.command == "run":
        for mode in valid_modes:
            if args.mode == mode["name"]:
                print_mode_warning(errors)
                print()

                terminal_title(mode)

                for i, operation_data in enumerate(
                    mode["operations"],
                    start=1
                ):
                    operation = create_operation(operation_data)
                    execute_operation(operation)
                    present_terminal(i, operation_data, operation)

                print("# End.")

    # Show
    if args.command == "show":
        for mode in valid_modes:
            if args.mode == mode["name"]:
                print_mode_warning(errors)
                print()

                print(f"Mode: {mode["name"]}")
                print(f"Description: {mode["description"] + "\n"}")

                for i, operation_data in enumerate(mode['operations'], start=1):
                    print(f"{operation_data['title']}:")
                    print(f"	Program: {operation_data['program']}")
                    print(f"	Arguments: {operation_data['args']}\n")

                print("# End.")

if __name__ == "__main__":
    mode_files = find_mode_files()
    valid_modes, errors = prepare_modes(mode_files)

    parser = build_parser(valid_modes)
    args = parser.parse_args()

    if not args.mode_errors and args.command is None:
        parser.print_help()
        sys.exit(0)

    main(args, valid_modes, errors)
