# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from getpass import getuser
from socket import gethostname
from datetime import datetime
from structure import ModeDict, OperationDict, HandlerResult

def terminal_title(mode: ModeDict) -> None:
    print(f"=== {mode["description"]} ===")
    print(f"# Runtime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"# User: {getuser()} | Device: {gethostname()}")

def present_terminal(i: int,
                     instruction: OperationDict,
                     operation: HandlerResult) -> None:
    """Preparing a report""" # TODO Full docstring.

    print(i, f"{instruction['title']}: {"OK" if operation.success is True else "FAIL"}:", operation.actual)
    print()
