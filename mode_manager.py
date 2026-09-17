# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path

from structure import ModeDict, OperationDict
from handler_manager import handler_names, find_handlers

BASE_DIR = Path(__file__).resolve().parent
MODE_DIR = BASE_DIR / "modes"

def find_mode_files() -> list[Path]:
    """Scans path for modes. Returns Path obj."""
    return list(MODE_DIR.glob("*.json"))

def load_mode(file: Path) -> ModeDict:
    """Loading configuration details. Returns dict[ModeDict]"""
    with file.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_mode_structure(mode_file: ModeDict) -> bool:
    """Checks whether the dictionary contains the required diagnostic keys and whether their values ​​have the correct types."""
    expected_structure: dict[str, type] = {
        "name": str,
        "description": str,
        "operations": list # list of OperationDict
    }

    for key, expected_type in expected_structure.items():
        if key not in mode_file:
            return False
        
        if not isinstance(mode_file[key], expected_type):
            return False

    if not all(isinstance(operation, dict) for operation in mode_file["operations"]):
        return False

    return True

def validate_operation_structure(operation: OperationDict) -> bool:
    """Checks the operation structure."""
    # TODO: Move handler-specific validation out of this function as the handler system develops.
    expected_structure: dict[str, type] = {
        "title": str,
        "program": str,
        "args": list,
        "handler": str,
    }

    handlers_with_expected: set[str] = {"equals", "contains"}

    for key, expected_type in expected_structure.items():
        if key not in operation:
            return False

        if not isinstance(operation[key], expected_type):
            return False

    if operation["handler"] in handlers_with_expected:
        if "expected" not in operation:
            return False

        if not isinstance(operation["expected"], str):
            return False
        
    if not all(isinstance(arg, str) for arg in operation["args"]):
        return False

    return True

def validate_operation_handler(operation: OperationDict) -> bool: # Coś lepszego trzeba wymyślić.
    handlers = handler_names(find_handlers())
    if not operation["handler"] in handlers:
        return False

    if not isinstance(operation["handler"], str):
        return False
    # In progress 
    return True

def prepare_modes(mode_files: list[Path]) -> tuple[list[ModeDict], list[str]]:
    """Checks JSON, mode structure and operation structures."""
    valid_modes:list[ModeDict] = []
    errors:list[str] = []

    for mode in mode_files:
        try:
            loaded_mode = load_mode(mode)
        except json.JSONDecodeError:
            message = (
                f"Mode: {mode} JSONDecodeError return Err\n"
                f"Check your {mode.name}"
            )
            errors.append(message)
            continue

        if not validate_mode_structure(loaded_mode):
            errors.append(f"Mode: {mode} has invalid structure")
            continue

        operations_valid = True

        for operation in loaded_mode["operations"]:
            if not validate_operation_structure(operation):
                operations_valid = False

                operation_name = operation.get("title", "<unknown operation>")
                errors.append(
                    f"Operation: {operation_name} has invalid structure"
                )

        if operations_valid:
            valid_modes.append(loaded_mode)

    return valid_modes, errors
