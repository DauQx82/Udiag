# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from getpass import getuser
from socket import gethostname
from datetime import datetime

from structure import ModeDict, OperationDict, OperationOutcome

def terminal_title(mode: ModeDict) -> None:
    print(f"=== {mode["description"]} ===")
    print(f"# Runtime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"# User: {getuser()} | Device: {gethostname()}")


def present_terminal(i: int,
                     instruction: OperationDict,
                     result: OperationOutcome) -> None:
    """Preparing a report""" # TODO Full docstring.
    if result[0] is True:
        print(i, f"{instruction['title']}: {"OK" if result[1].success is True else "FAIL"}:", result[1].actual)
        print()

    else:
        print(i, f"{instruction['title']}: ERROR, reason: {result[1]}")
