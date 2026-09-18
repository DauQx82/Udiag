# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from types import ModuleType
from typing import Literal, Union
import importlib.util

HANDLERS_DIR = Path(__file__).resolve().parent / "handlers"

INIT_FILE = HANDLERS_DIR / "__init__.py"
HANDLER_FILE = HANDLERS_DIR / "handler.py"

def _validate_handler_lookup() -> tuple[bool, str]:
    """Return True if valid, else False, message"""
    if not INIT_FILE.is_file():
        message = "The __init__.py file was not found."
        return False, message

    if not HANDLER_FILE.is_file():
        message = "The handler.py file was not found."
        return False, message

    return True, ""

FindHandlersSuccess = tuple[Literal[True], list[Path]]
FindHandlersFailure = tuple[Literal[False], str]
FindHandlersResult = Union[FindHandlersSuccess, FindHandlersFailure]

def find_handlers() -> FindHandlersResult:
    handlers: list[Path] = []
    is_valid, message = _validate_handler_lookup()

    if not is_valid:
        return False, message

    handlers = [handler for handler in HANDLERS_DIR.glob("*.py") if handler not in (INIT_FILE, HANDLER_FILE)]
    return True, handlers

BuildMapSuccess = tuple[Literal[True], dict[str, Path]]
BuildMapFailure = tuple[Literal[False], str]
BuildMapResult = Union[BuildMapSuccess, BuildMapFailure]

def build_handler_map(handler_input: FindHandlersResult) -> BuildMapResult:
    handlers: dict[str, Path] = {}

    if handler_input[0] is False:
        message = f"Failed to build the map: '{handler_input[1]}'"
        return False, message

    handler_list = handler_input[1]

    for handler in handler_list:
        handlers[handler.stem] = handler
    return True, handlers

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
