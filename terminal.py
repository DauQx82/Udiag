# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from getpass import getuser
from socket import gethostname
from datetime import datetime
from typing import Literal

from structure import ModeDict, OperationDict, OperationOutcome

type OperationStatus = Literal["OK", "FAIL", "ERROR"]

GREEN = "\033[32m"
RED_WARNING = "\033[91m"
RED_ERROR = "\033[31m"
RESET = "\033[0m"

def operation_status(result: OperationOutcome) -> OperationStatus:
    if result[0] is False:
        return "ERROR"

    if result[1].success is False:
        return "FAIL"

    return "OK"

STATUS_LABELS = {
    "OK": f"[{GREEN}SUCCESS{RESET}]",
    "FAIL": f"[{RED_WARNING}FAILURE{RESET}]",
    "ERROR": f"[{RED_ERROR} ERROR {RESET}]"
}

def terminal_title(mode: ModeDict,
                   with_details: bool = False) -> None:
    print(f"=== {mode["description"]} ===")
    print(f"# Runtime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    if with_details:
        print(f"# User: {getuser()} | Device: {gethostname()}")


def present_list(i: int,
                 instruction: OperationDict,
                 result: OperationOutcome,
                 with_details: bool = False) -> None:
    """Present an operation result in terminal output."""
    status = operation_status(result)

    if with_details:
        if status == "OK" and result[0] is True:
            print()
            print("    ", STATUS_LABELS[status], instruction["title"])
            print("    " * 2, "Actual value: ", result[1].actual)
            print("    " * 2, "Expected: ", result[1].expected)

    else:
        print("\n" if i == 1 else "", end="")
        if status == "OK":
            print("    ", STATUS_LABELS[status], instruction["title"])

    if status == "FAIL" and result[0] is True:
        print()
        print("    ", STATUS_LABELS[status], instruction["title"])
        print("    " * 2, "Actual value: ", result[1].actual)
        print("    " * 2, "Expected: ", result[1].expected)

    elif status == "ERROR":
        print()
        print("    ", STATUS_LABELS[status], instruction["title"])
        print("    " * 2, "Exception: ", result[1])
