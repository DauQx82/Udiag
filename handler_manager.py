# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

HANDLERS_DIR = Path(__file__).resolve().parent / "handlers"

def find_handlers() -> list[Path]:
    return list(HANDLERS_DIR.glob("*.py"))

def handlers_name(handlers: list[Path]) -> list[str]:
    """Prepares a list of available handlers and returns their names [str], or false if no handlers could be found."""
    handler_names: list[str] = [handler.stem for handler in handlers]
    return handler_names