# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from .handler import BaseHandler
from structure import HandlerResult


class PassHandler(BaseHandler):
    @classmethod
    def validate_config(cls, config: object) -> bool:
        return config is True

    def evaluate(self) -> HandlerResult:
        return HandlerResult(
            success=True,
            actual=self.actual,
            expected=None,
        )