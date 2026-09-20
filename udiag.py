# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import argparse
import sys

from mode_manager import prepare_modes, find_mode_files
from structure import (
    ModeDict,
    Operation,
    OperationResult,
    create_operation
)

from handler_manager import (
    find_handlers,
    build_handler_map,
    build_handler_registry,
)
from handlers.handler import BaseHandler
from terminal import present_terminal, terminal_title
from state import errors

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


def print_mode_warning() -> None: # TODO
    if errors.count > 0:
        print()
        print(f"{errors.count} Errors")
        print("For details, run udiag.py -e, --errors" + "\n")


def print_mode_errors() -> None: # TODO
    if errors.handler:
        print(f"Number of handler errors: {len(errors.handler)}")
        print("Details:" + "\n")

        for i, error in enumerate(errors.handler, start=1):
            print(f"{i}. {error}")

        print()
        print("#" * 30)
        if not errors.mode:
            return
        print()

    if errors.mode:
        print(f"Number of mode errors: {len(errors.mode)}")
        print("Details:" + "\n")

        for i, error in enumerate(errors.mode, start=1):
            print(f"{i}. {error}")

        return
    print("No errors.")


def execute_operation(operation: Operation) -> OperationResult:
    result = subprocess.run([operation.program, *operation.args],
                            capture_output=True,
                            text=True,
                            timeout=10) # TODO A timeout became a normal operation 
                                        # result/error instead of terminating the program.

    operation_result = OperationResult(
        result.stdout,
        result.stderr,
        result.returncode
    )
    return operation_result

def main(args,
         registry: dict[str, type[BaseHandler]],
         valid_modes: list[ModeDict]) -> None:
    # Errors FIXME
    if args.mode_errors:
        print_mode_errors()
        return
    
    # Run
    if args.command == "run":
        for mode in valid_modes:
            if args.mode == mode["name"]:
                print_mode_warning()
                print()

                terminal_title(mode)

                for i, operation_data in enumerate(
                    mode["operations"],
                    start=1
                ):
                    operation = create_operation(operation_data)
                    operation_result = execute_operation(operation)
                    handler_name = operation_data["handler"]
                    handler_class = registry[handler_name]

                    handler = handler_class(
                        operation_result,
                        operation_data.get("expected")
                    )

                    handler_result = handler.evaluate()
                    present_terminal(i, operation_data, handler_result)

                print("# End.")

    # Show
    if args.command == "show":
        for mode in valid_modes:
            if args.mode == mode["name"]:
                print_mode_warning()
                print()

                print(f"Mode: {mode["name"]}")
                print(f"Description: {mode["description"] + "\n"}")

                for i, operation_data in enumerate(mode['operations'], start=1):
                    print(f"{operation_data['title']}:")
                    print(f"	Program: {operation_data['program']}")
                    print(f"	Arguments: {operation_data['args']}\n")

                print("# End.")


if __name__ == "__main__":
    handlers = find_handlers()

    if handlers[0] is False:
        print(handlers[1])
        sys.exit(1)

    handler_map = build_handler_map(handlers)
    registry, handler_errors = build_handler_registry(handler_map)
    errors.handler = handler_errors

    if not registry:
        print("No valid handlers available.")
        sys.exit(1)

    mode_files = find_mode_files()
    valid_modes, mode_errors = prepare_modes(mode_files, registry)
    errors.mode = mode_errors

    parser = build_parser(valid_modes)
    args = parser.parse_args()

    if not args.mode_errors and args.command is None:
        parser.print_help()
        sys.exit(0)

    main(args,registry, valid_modes) # FIXME Teraz mam dataclass, to nie muszę tego przekazywać.
