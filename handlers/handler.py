# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from structure import HandlerResult

type CheckValue = str | int

class BaseHandler(ABC):
    def __init__(
        self,
        actual: CheckValue,
        config: object,
    ) -> None:
        self.actual = actual
        self.config = config

    @classmethod
    @abstractmethod
    def validate_config(cls, config: object) -> bool:
        pass

    @abstractmethod
    def evaluate(self) -> HandlerResult:
        pass