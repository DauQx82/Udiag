# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from structure import OperationDict, OperationResult, HandlerResult

class BaseHandler(ABC):
    def __init__(self,
                 result: OperationResult,
                 expected: str | None) -> None:
        self.result = result
        self.expected = expected

    @classmethod
    @abstractmethod
    def validate_config(cls, operation: OperationDict) -> bool:
        pass

    @abstractmethod
    def evaluate(self) -> HandlerResult:
        pass

