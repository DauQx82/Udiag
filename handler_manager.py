# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from types import ModuleType
from typing import Literal, Union
import importlib.util
import inspect

from handlers.handler import BaseHandler

HANDLERS_DIR = Path(__file__).resolve().parent / "handlers"

INIT_FILE = HANDLERS_DIR / "__init__.py"
HANDLER_FILE = HANDLERS_DIR / "handler.py"

def _validate_handler_lookup() -> tuple[bool, str]:
    """
    Check whether the required handler infrastructure files exist.

    Return a success flag and an error message if validation fails.
    """
    if not INIT_FILE.is_file():
        message = "The __init__.py file was not found."
        return False, message

    if not HANDLER_FILE.is_file():
        message = "The handler.py file was not found."
        return False, message

    return True, ""

type FindHandlersSuccess = tuple[Literal[True], list[Path]]
type FindHandlersFailure = tuple[Literal[False], str]
type FindHandlersResult = Union[FindHandlersSuccess, FindHandlersFailure]

def find_handlers() -> FindHandlersResult:
    """
    Discover handler implementation files in the handlers directory.

    Infrastructure files such as __init__.py and handler.py are excluded.
    """
    handlers: list[Path] = []
    is_valid, message = _validate_handler_lookup()

    if not is_valid:
        return False, message

    handlers = [handler for handler in HANDLERS_DIR.glob("*.py") if handler not in (INIT_FILE, HANDLER_FILE)]
    return True, handlers


def build_handler_map(handler_input: FindHandlersSuccess) -> dict[str, Path]:
    """
    Build a name-to-path mapping from successfully discovered handler files.

    The function assumes handler discovery has already succeeded.
    """
    handlers: dict[str, Path] = {}

    for handler in handler_input[1]:
        handlers[handler.stem] = handler
    return handlers


type LoadHandlerSuccess = tuple[Literal[True], ModuleType]
type LoadHandlerFailure = tuple[Literal[False], str]
type LoadHandlerResult = Union[LoadHandlerSuccess, LoadHandlerFailure]

def load_handler(handler_file: Path) -> LoadHandlerResult:
    """
    Dynamically load a handler module from the provided file path.

    Return the loaded module on success or an error message on failure.
    """
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


type FindHandlerClassSuccess = tuple[Literal[True], type[BaseHandler]]
type FindHandlerClassFailure = tuple[Literal[False], str]
type FindHandlerClassResult = Union[FindHandlerClassSuccess, FindHandlerClassFailure]

def find_handler_class(module: ModuleType) -> FindHandlerClassResult:
    """
    Locate the single BaseHandler subclass defined by the module.

    Fail if none is found, more than one exists, or the class is abstract.
    """
    classes = inspect.getmembers(module, inspect.isclass)
    handler_candidates: list[type[BaseHandler]] = []

    if not classes:
        return False, f"No classes found in module: '{module.__name__}'"

    for _, candidate in classes:
        if issubclass(candidate, BaseHandler):
            if (
                candidate is not BaseHandler and
                candidate.__module__ == module.__name__
                ):
                    handler_candidates.append(candidate)

    if not handler_candidates:
        return False, f"No BaseHandler subclass found in module '{module.__name__}'."

    if len(handler_candidates) > 1:
        return False, (
            f"Found {len(handler_candidates)} BaseHandler subclasses "
            f"in module '{module.__name__}'; expected exactly one."
        )

    if inspect.isabstract(handler_candidates[0]):
        return False, (
            f"Handler class '{handler_candidates[0].__name__}' in '{handler_candidates[0].__module__}' is abstract\n"
            f"Missing implementations: {handler_candidates[0].__abstractmethods__}"
        )

    return True, handler_candidates[0]


def build_handler_registry(handlers_map: dict[str, Path]) -> tuple[dict[str, type[BaseHandler]], list[str]]:
    """
    Build a registry of valid handler classes from a name-to-path mapping.

    Invalid handlers are skipped and their errors are collected.
    """
    handler_registry: dict[str, type[BaseHandler]] = {}
    errors: list[str] = []

    for name, path in handlers_map.items():
        loaded_handlers = load_handler(path)

        if loaded_handlers[0] is True:
            is_class_valid = find_handler_class(loaded_handlers[1])

            if is_class_valid[0] is True:
                handler_registry[name] = is_class_valid[1]

            else:
                errors.append(is_class_valid[1])

        else:
            errors.append(loaded_handlers[1])
    return handler_registry, errors
