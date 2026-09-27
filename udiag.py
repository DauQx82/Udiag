# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import argparse
import sys

from mode_manager import prepare_modes, find_mode_files
from structure import (
    ValidatedMode,
    CheckSkeleton,
    CheckResult,
    Operation,
    OperationResult,
    EvaluatedOperation,
    OperationExecutionError,
    create_operation,
)

from handler_manager import (
    find_handlers,
    build_handler_map,
    build_handler_registry,
)
from handlers.handler import BaseHandler
from terminal import terminal_title, present_list
from state import errors


def get_mode_names(modes: list[ValidatedMode]) -> list[str]:
    """Prepares a list of arguments for each specific mode."""
    args_list: list[str] = []
    for mode_files in modes:
        args_list.append(mode_files["name"])

    return args_list


def build_parser(valid_modes: list[ValidatedMode]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Udiag - Declarative diagnostic scenario runner"
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

    run_parser.add_argument(
        "--details",
        action="store_true"
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

    # List
    subparsers.add_parser(
        "list",
        help="List available diagnostic modes"
    )

    # About
    subparsers.add_parser(
        "about",
        help="Show information about Udiag"
    )

    return parser

def print_mode_warning() -> None:
    if errors.count > 0:
        print()
        print(f"{errors.count} Errors")
        print("For details, run udiag.py -e, --errors" + "\n")


def print_mode_errors() -> None:
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


def print_mode_list(
    valid_modes: list[ValidatedMode],
) -> None:
    if not valid_modes:
        print("No diagnostic modes available.")
        return

    print("Available diagnostic modes:")
    print()

    for mode in valid_modes:
        print(f"  {mode['name']}")
        print(f"    {mode['description']}")


def print_about() -> None:
    print("Udiag")
    print("Declarative diagnostic scenario runner")
    print()
    print("License: GPL-3.0-or-later")


def execute_operation(operation: Operation) -> OperationResult:
    result = subprocess.run([operation.program, *operation.args],
                            capture_output=True,
                            text=True,
                            timeout=10)

    operation_result = OperationResult(
        result.stdout,
        result.stderr,
        result.returncode
    )
    return operation_result


def get_check_value(result: OperationResult, source: str) -> str | int:
    if source == "stdout":
        return result.stdout

    if source == "stderr":
        return result.stderr

    if source == "returncode":
        return result.returncode

    raise ValueError(f"Unsupported source: {source}")


def evaluate_checks(
    operation_result: OperationResult,
    checks: list[CheckSkeleton],
    registry: dict[str, type[BaseHandler]],
) -> list[CheckResult]:
    results: list[CheckResult] = []

    for check in checks:
        actual = get_check_value(
            operation_result,
            check["source"],
        )

        handler_class = registry[check["handler"]]

        handler = handler_class(
            actual,
            check["config"],
        )
        handler_result = handler.evaluate()

        check_result = CheckResult(
            source=check["source"],
            handler=check["handler"],
            result=handler_result,
        )
        results.append(check_result)

    return results

def main(args,
         registry: dict[str, type[BaseHandler]],
         valid_modes: list[ValidatedMode]) -> None:
    # Errors FIXME
    if args.mode_errors:
        print_mode_errors()
        return

    if args.command == "list":
        print_mode_list(valid_modes)
        return

    if args.command == "about":
        print_about()
        return


    # Run
    if args.command == "run":
        for mode in valid_modes:
            if args.mode == mode["name"]:
                print_mode_warning()
                print()

                terminal_title(mode, args.details)

                for i, operation_data in enumerate(
                    mode["operations"],
                    start=1
                ):
                    operation = create_operation(operation_data)
                    try:
                        operation_result = execute_operation(operation)
                    except (
                        FileNotFoundError,
                        PermissionError,
                        subprocess.TimeoutExpired
                    ) as error:
                        outcome = OperationExecutionError(error=error)

                    else:
                        check_results = evaluate_checks(
                            operation_result,
                            operation_data["checks"],
                            registry,
                        )

                        outcome = EvaluatedOperation(
                            process_result=operation_result,
                            check_results=check_results,
                        )
                    present_list(i, operation_data, outcome, args.details)

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

    main(args, registry, valid_modes)

# TODO: Future: SKIP outcome for conditional/precondition-based operations.
