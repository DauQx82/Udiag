# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from getpass import getuser
from socket import gethostname
from datetime import datetime
from typing import Literal

from structure import (
    ValidatedMode,
    ValidatedOperation,
    OperationOutcome,
    OperationExecutionError,
    SkippedOperation
)

type OperationStatus = Literal["OK", "FAIL", "ERROR", "SKIP"]

GREEN = "\033[32m"
RED_WARNING = "\033[91m"
RED_ERROR = "\033[31m"
RESET = "\033[0m"

def operation_status(result: OperationOutcome) -> OperationStatus:
    if isinstance(result, OperationExecutionError):
        return "ERROR"

    if isinstance(result, SkippedOperation):
        return "SKIP"

    if result.success is False:
        return "FAIL"

    return "OK"

STATUS_LABELS = {
    "OK": f"[{GREEN}SUCCESS{RESET}]",
    "FAIL": f"[{RED_WARNING}FAILURE{RESET}]",
    "ERROR": f"[{RED_ERROR} ERROR {RESET}]",
    "SKIP": f"[{RED_ERROR} SKIP {RESET}]"
}

def terminal_title(mode: ValidatedMode,
                   with_details: bool = False) -> None:
    print(f"=== {mode["description"]} ===")
    print(f"# Runtime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    if with_details:
        print(f"# User: {getuser()} | Device: {gethostname()}")


def present_list(
    i: int,
    instruction: ValidatedOperation,
    result: OperationOutcome,
    with_details: bool = False,
) -> None:
    """Present an operation result in terminal output."""
    status = operation_status(result)

    print("\n" if i == 1 else "", end="")
    print("    ", STATUS_LABELS[status], instruction["title"])

    if isinstance(result, OperationExecutionError):
        print("    " * 2, "Exception:", result.error)
        return

    if isinstance(result, SkippedOperation):
        print("    " * 2, "Reason:", result.reason)
        return

    if status == "FAIL":
        for check in result.check_results:
            if check.result.success:
                continue

            print("    " * 2, f"{check.source} / {check.handler}")
            print("    " * 3,"Actual value:", check.result.actual)
            print("    " * 3, "Expected:", check.result.expected)
        return

    if with_details:
        for check in result.check_results:
            print("    " * 2, f"{check.source} / {check.handler}")
            print("    " * 3, "Actual value:", check.result.actual)
            print("    " * 3, "Expected:", check.result.expected)