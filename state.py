# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass, field


@dataclass
class Errors:
    handler: list[str] = field(default_factory=list)
    mode: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.handler) + len(self.mode)


errors = Errors()