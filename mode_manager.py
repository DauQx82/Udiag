# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from collections.abc import Mapping
from typing import cast

from structure import ModeDict, OperationDict
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


def validate_mode_structure(mode_file: dict) -> bool:
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
        
    if not mode_file["operations"]:
        return False

    if not all(isinstance(operation, dict) for operation in mode_file["operations"]):
        return False

    return True


def validate_operation_structure(operation: dict) -> bool:
    """Checks the operation structure."""
    expected_structure: dict[str, type] = {
        "title": str,
        "program": str,
        "args": list,
        "handler": str,
    }

    for key, expected_type in expected_structure.items():
        if key not in operation:
            return False

        if not isinstance(operation[key], expected_type):
            return False

    if not operation["program"].strip():
        return False

    if not all(isinstance(arg, str) for arg in operation["args"]):
        return False

    return True


def validate_operation_handler(operation: OperationDict,
                               registry: Mapping[str, type[BaseHandler]]) -> bool:
    handler_name = operation["handler"]

    if handler_name not in registry:
        return False

    handler_class = registry[handler_name]
    return handler_class.validate_config(operation)


def prepare_modes(mode_files: list[Path],
                  registry: Mapping[str, type[BaseHandler]]) -> tuple[list[ModeDict], list[str]]:
    """Checks JSON, mode structure and operation structures."""
    valid_modes:list[ModeDict] = []
    errors:list[str] = []

    for mode in mode_files:
        try:
            loaded_json = load_mode(mode)
        except json.JSONDecodeError:
            message = (
                f"Mode: {mode} JSONDecodeError return Err\n"
                f"Check your {mode.name}"
            )
            errors.append(message)
            continue

        if not isinstance(loaded_json, dict):
            errors.append("mode is not dict type, or something.")
            continue

        if not validate_mode_structure(loaded_json):
            errors.append(f"Mode: {mode} has invalid structure")
            continue

        operations_valid = True

        for operation in loaded_json["operations"]:
            if not validate_operation_structure(operation):
                operations_valid = False

                operation_name = operation.get("title", "<unknown operation>")
                errors.append(
                    f"Operation: {operation_name} has invalid structure"
                )
                continue

            operation_dict = cast(OperationDict, operation)

            if not validate_operation_handler(operation_dict, registry):
                operations_valid = False

                operation_name = operation["title"]
                errors.append(
                    f"Operation: {operation_name} failed handler validation"
                )

        if operations_valid:
            mode_dict = cast(ModeDict, loaded_json)
            valid_modes.append(mode_dict)

    return valid_modes, errors
