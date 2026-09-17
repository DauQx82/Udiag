# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from types import ModuleType
import importlib.util

HANDLERS_DIR = Path(__file__).resolve().parent / "handlers"

def find_handlers() -> list[Path]:
    return list(HANDLERS_DIR.glob("*.py"))

def handler_names(handlers: list[Path]) -> list[str]:
    """Prepares a list of available handlers and returns their names [str], or false if no handlers could be found."""
    handler_names: list[str] = [handler.stem for handler in handlers]
    return handler_names

def load_handler(handler_file: Path) -> tuple[bool, ModuleType | str]:
    """Check and if valid, load handler"""
    handler_name = f"handlers.{handler_file.stem}"
    spec = importlib.util.spec_from_file_location(handler_name, handler_file)

    if spec is None:
        message = f"Could not create module spec for handler: {handler_name}"
        return False, message

    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        message = f"No loader available for handler: {handler_name}"
        return False, message

    try:
        spec.loader.exec_module(module)

    except Exception as e:
        message = f"Failed to load handler '{handler_name}': {e}"
        return False, message

    return True, module
