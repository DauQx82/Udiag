# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import cast

from .handler import BaseHandler
from structure import HandlerResult


class EqualsHandler(BaseHandler):
    @classmethod
    def validate_config(cls, config: object) -> bool:
        return type(config) in (str, int)

    def evaluate(self) -> HandlerResult:
        expected = cast(str | int, self.config)
        actual = self.actual

        if isinstance(actual, str):
            actual = actual.rstrip("\r\n")

        return HandlerResult(
            success=actual == expected,
            actual=actual,
            expected=expected,
        )