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
    Check whether the required handler package files exist.
    Return a success flag and an error message when validation fails.
    """
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

BuildMapSuccess = tuple[Literal[True], dict[str, Path]]
BuildMapFailure = tuple[Literal[False], str]
BuildMapResult = Union[BuildMapSuccess, BuildMapFailure]

def build_handler_map(handler_input: FindHandlersResult) -> BuildMapResult:
    """
    Build a mapping from handler names to their source file paths.
    Propagate the discovery error if handler lookup failed.
    """
    handlers: dict[str, Path] = {}

    if handler_input[0] is False:
        message = f"Failed to build the map: '{handler_input[1]}'"
        return False, message

    handler_list = handler_input[1]

    for handler_path in handler_list:
        handlers[handler_path.stem] = handler_path
    return True, handlers

LoadHandlerSuccess = tuple[Literal[True], ModuleType]
LoadHandlerFailure = tuple[Literal[False], str]
LoadHandlerResult = Union[LoadHandlerSuccess, LoadHandlerFailure]

def load_handler(handler_file: Path) -> LoadHandlerResult:
    """
    Load a handler module dynamically from the provided file path.
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

FindHandlerClassSuccess = tuple[Literal[True], type[BaseHandler]]
FindHandlerClassFailure = tuple[Literal[False], str]
FindHandlerClassResult = Union[FindHandlerClassSuccess, FindHandlerClassFailure]

def find_handler_class(module: ModuleType) -> FindHandlerClassResult:
    """
    Locate the single concrete BaseHandler subclass defined by a module.
    Fail if no valid subclass exists, more than one is found, or it is abstract.
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

def build_handler_registry(handlers_map: BuildMapSuccess) -> tuple[dict[str, type[BaseHandler]], list[str]]:
    """
    Build a registry of valid handler classes from discovered handler files.
    Invalid handlers are skipped and their errors are collected.
    """
    handler_registry: dict[str, type[BaseHandler]] = {}
    errors: list[str] = []

    for name, path in handlers_map[1].items():
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

if __name__ == "__main__":
    handlers = find_handlers()
    mymap = build_handler_map(handlers) # nazwa: Path

    if mymap[0] is True:
        build_handler_registry(mymap)

ValidatePipelineSuccess = tuple[dict[str, type[BaseHandler]], list[str]]
ValidatePipelineFailure = tuple[Literal[False], list[str]]
ValidatePipelineResult = Union[ValidatePipelineSuccess, ValidatePipelineFailure]

def validate_pipeline(search_result: FindHandlersResult) -> ValidatePipelineResult:
    """
    Run the handler discovery and registration pipeline.
    Return the available handler registry with collected errors, or a critical failure.
    """
    errors: list[str] = []
    registry: dict[str, type[BaseHandler]] = {}
    _build_handler_map = build_handler_map(search_result)

    if _build_handler_map[0] is True:
        _build_handler_registry = build_handler_registry(_build_handler_map)
        registry = _build_handler_registry[0]
        errors.extend(_build_handler_registry[1])

    else:
        errors.append(_build_handler_map[1])
        errors.append("Critical Failure: 'The registry cannot be built; the program fails to start.' ")
        return False, errors

    if not registry:
        errors.append("Critical Failure: 'The registry failed to built; the program fails to start.' ")
        return False, errors
    return registry, errors
