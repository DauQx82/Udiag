# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from .handler import BaseHandler
from structure import HandlerResult


class EmptyHandler(BaseHandler):
    @classmethod
    def validate_config(cls, config: object) -> bool:
        return config is True

    def evaluate(self) -> HandlerResult:
        actual = self.actual

        if isinstance(actual, str):
            normalized = actual.rstrip("\r\n")
            success = normalized == ""
            actual = normalized
        else:
            success = False

        return HandlerResult(
            success=success,
            actual=actual,
            expected="",
        )
