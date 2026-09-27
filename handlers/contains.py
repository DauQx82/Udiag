# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import cast

from .handler import BaseHandler
from structure import HandlerResult


class ContainsHandler(BaseHandler):
    @classmethod
    def validate_config(cls, config: object) -> bool:
        return isinstance(config, str)

    def evaluate(self) -> HandlerResult:
        expected = cast(str, self.config)
        actual = self.actual

        success = (
            isinstance(actual, str)
            and expected in actual
        )

        return HandlerResult(
            success=success,
            actual=actual,
            expected=expected,
        )
