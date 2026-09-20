# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import cast

from .handler import BaseHandler
from structure import OperationResult, HandlerResult

class EqualsHandler(BaseHandler):
    def __init__(self, result: OperationResult, expected: str | None) -> None:
        super().__init__(result, expected)

    @classmethod
    def validate_config(cls, operation) -> bool:
        if "expected" not in operation:
            return False

        if not isinstance(operation["expected"], str):
            return False
        
        return True

    def evaluate(self) -> HandlerResult:
        expected = cast(str, self.expected)
        actual = self.result.stdout.rstrip("\r\n")

        return HandlerResult(
            success=actual == expected,
            actual=actual,
            expected=expected
        )
