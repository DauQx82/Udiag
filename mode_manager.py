# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from collections.abc import Mapping
from typing import (
    cast,
    Literal,
    Union,
    TypedDict,
    Any
)

from handlers.handler import BaseHandler

BASE_DIR = Path(__file__).resolve().parent
MODE_DIR = BASE_DIR / "modes"

def find_mode_files() -> list[Path]:
    """Scans path for modes. Returns Path obj."""
    return list(MODE_DIR.glob("*.json"))


def load_mode(file: Path) -> object:
    """Loading configuration details. Returns object"""
    with file.open("r", encoding="utf-8") as f:
        return json.load(f)


class ModeSkeleton(TypedDict):
    name: str
    description: str
    operations: list[dict[str, object]]

type ValidateModeStructureSuccess = tuple[Literal[True], ModeSkeleton]
type ValidateModeStructureFailure = tuple[Literal[False], str]
type ValidateModeStructureResult = Union[ValidateModeStructureSuccess, ValidateModeStructureFailure]

def validate_mode_structure(mode_file: dict[Any, Any]) -> ValidateModeStructureResult:
    """Checks whether the dictionary contains the required diagnostic keys and whether their values ​​have the correct types."""
    expected_structure: dict[str, type] = {
        "name": str,
        "description": str,
        "operations": list # list of OperationDict
    }

    for key, expected_type in expected_structure.items():
        if key not in mode_file:
            return False, f"Mode has no: {key} in scenario."
        
        if not isinstance(mode_file[key], expected_type):
            return False, f"Type of {mode_file[key]} is not supported."
        
    if not mode_file["operations"]:
        return False, "No operations."

    if not all(isinstance(operation, dict) for operation in mode_file["operations"]):
        return False, "Operation invalid structure."

    valid_mode: ModeSkeleton = {
        "name": mode_file['name'],
        "description": mode_file['description'],
        "operations": mode_file['operations']
    }
    return True, valid_mode


class OperationSkeleton(TypedDict):
    title: str
    program: str
    args: list[str]
    checks: dict[str, object]

type ValidateOperationSuccess = tuple[Literal[True], OperationSkeleton]
type ValidateOperationFailure = tuple[Literal[False], str]
type ValidateOperationResult = Union[ValidateOperationSuccess, ValidateOperationFailure]

def validate_operation_structure(operation: dict[Any, Any]) -> ValidateOperationResult:
    """Checks the operation structure."""
    expected_structure: dict[str, type] = {
        "title": str,
        "program": str,
        "args": list,
        "checks": dict,
    }

    for key, expected_type in expected_structure.items():
        if key not in operation:
            return False, f"Operation has no: {key} in structure."

        if not isinstance(operation[key], expected_type):
            return False, f"Type of {operation[key]} is not supported."

    if not operation["checks"]:
        return False, "No 'checks' section."

    if not operation["program"].strip():
        return False, "Program field is empty."

    if not all(isinstance(arg, str) for arg in operation["args"]):
        return False, "Type of arg: is not supported."

    valid_operation: OperationSkeleton = {
        "title": operation['title'],
        "program": operation['program'],
        "args": operation['args'],
        "checks": operation['checks']
    }

    return True, valid_operation


type CheckSource = Literal["stdout", "stderr", "returncode"]

class CheckSkeleton(TypedDict):
    source: CheckSource
    handler: str
    config: object

type ValidateChecksStructureSuccess = tuple[Literal[True], list[CheckSkeleton]]
type ValidateChecksStructureFailure = tuple[Literal[False], str]
type ValidateChecksStructureResult = Union[ValidateChecksStructureSuccess, ValidateChecksStructureFailure]

def validate_checks_structure(operation: OperationSkeleton) -> ValidateChecksStructureResult:
    """Checks the structure of operation checks."""
    allowed_sources: set[CheckSource] = {"stdout", "stderr", "returncode"}
    checks = operation["checks"]

    valid_checks: list[CheckSkeleton] = []

    for source, handlers in checks.items():
        if source not in allowed_sources:
            return False, "Source of data in not supported."

        if not isinstance(handlers, dict):
            return False, "Invalid structure of handler/s instruction."

        if not handlers:
            return False, "No handler/s instructions."

        valid_source = cast(CheckSource, source)

        for handler_name, config in handlers.items():
            valid_check: CheckSkeleton = {
                "source": valid_source,
                "handler": handler_name,
                "config": config
            }
            valid_checks.append(valid_check)

    return True, valid_checks


def validate_handler(
    handler_name: str,
    config: object,
    registry: Mapping[str, type[BaseHandler]],
) -> bool:
    """"""
    if handler_name not in registry:
        return False

    handler_class = registry[handler_name]
    return handler_class.validate_config(config)


type ValidateChecksSuccess = tuple[Literal[True], list[CheckSkeleton]]
type ValidateChecksFailure = tuple[Literal[False], str]
type ValidateChecksResult = Union[ValidateChecksSuccess, ValidateChecksFailure]

def validate_checks(
    checks: list[CheckSkeleton],
    registry: Mapping[str, type[BaseHandler]],
) -> ValidateChecksResult:
    """"""
    for check in checks:
        if not validate_handler(
            check["handler"],
            check["config"],
            registry
        ):
            return False, (
                f"Invalid handler '{check['handler']}' "
                f"for source '{check['source']}'."
            )

    return True, checks


class ValidatedOperation(TypedDict):
    title: str
    program: str
    args: list[str]
    checks: list[CheckSkeleton]

class ValidatedMode(TypedDict):
    name: str
    description: str
    operations: list[ValidatedOperation]

def prepare_modes(
    mode_files: list[Path],
    registry: Mapping[str, type[BaseHandler]],
) -> tuple[list[ValidatedMode], list[str]]:
    """Loads modes, validates their structure and prepares valid operations."""
    valid_modes: list[ValidatedMode] = []
    errors: list[str] = []

    for mode in mode_files:
        try:
            loaded_json = load_mode(mode)
        except json.JSONDecodeError:
            errors.append(f"Mode: {mode} contains invalid JSON.")
            continue

        if not isinstance(loaded_json, dict):
            errors.append(f"Mode: {mode} root JSON value must be an object.")
            continue

        mode_result = validate_mode_structure(loaded_json)

        if mode_result[0] is False:
            errors.append(f"Mode: {mode}: {mode_result[1]}")
            continue

        valid_operations: list[ValidatedOperation] = []

        for raw_operation in mode_result[1]["operations"]:
            operation_result = validate_operation_structure(raw_operation)

            if operation_result[0] is False:
                operation_name = raw_operation.get(
                    "title",
                    "<unknown operation>",
                )

                errors.append(
                    f"Mode: {mode.name}, "
                    f"operation: {operation_name}: "
                    f"{operation_result[1]}"
                )
                continue

            operation_skeleton = operation_result[1]
            checks_structure_result = validate_checks_structure(operation_skeleton)

            if checks_structure_result[0] is False:
                errors.append(
                    f"Mode: {mode.name}, "
                    f"operation: {operation_skeleton['title']}: "
                    f"{checks_structure_result[1]}"
                )
                continue

            checks = checks_structure_result[1]
            checks_result = validate_checks(checks, registry)

            if checks_result[0] is False:
                errors.append(
                    f"Mode: {mode.name}, "
                    f"operation: {operation_skeleton['title']}: "
                    f"{checks_result[1]}"
                )
                continue

            valid_operation: ValidatedOperation = {
                "title": operation_skeleton["title"],
                "program": operation_skeleton["program"],
                "args": operation_skeleton["args"],
                "checks": checks_result[1],
            }
            valid_operations.append(valid_operation)

        if not valid_operations:
            errors.append(f"Mode: {mode.name} contains no valid operations.")
            continue

        valid_mode: ValidatedMode = {
            "name": mode_result[1]["name"],
            "description": mode_result[1]["description"],
            "operations": valid_operations,
        }
        valid_modes.append(valid_mode)

    return valid_modes, errors
