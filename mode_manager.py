import json
from pathlib import Path

from structure import ModeDict, OperationDict

BASE_DIR = Path(__file__).resolve().parent
MODE_DIR = BASE_DIR / "modes"


def scan_config() -> list[Path]:
    """Scans path for modes. Returns Path obj."""
    return list(MODE_DIR.glob("*.json"))

def load_mode(file: Path) -> ModeDict:
    """Loading configuration details. Returns dict[ModeDict]"""
    with file.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_json(file: Path) -> bool:
    """Return true if json has no errors"""
    try:
        load_mode(file)
    except json.JSONDecodeError:
        return False
    
    return True

def validate_mode_structure(mode: ModeDict) -> bool:
    """Checks whether the dictionary contains the required diagnostic keys and whether their values ​​have the correct types."""
    expected_structure: dict[str, type] = {
        "name": str,
        "description": str,
        "operations": list # list of OperationDict
    }

    for key, expected_type in expected_structure.items():
        if key not in mode:
            return False
        
        if not isinstance(mode[key], expected_type):
            return False

    if not all(isinstance(operation, dict) for operation in mode["operations"]):
        return False

    return True

def validate_operation_structure(operation: OperationDict) -> bool:
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

def prepare_modes() -> tuple[list[ModeDict], list[str]]:
    """Checks JSON, mode structure and operation structures."""
    modes = scan_config()
    loaded_json:list[ModeDict] = []
    err_list:list[str] = []

    for mode in modes:
        if not validate_json(mode):
            message = (
                f"Mode: {mode} JSONDecodeError return Err\n"
                f"Check your {mode.name}"
            )
            err_list.append(message)
            continue

        loaded = load_mode(mode)

        if not validate_mode_structure(loaded):
            err_list.append(f"Mode: {mode} has invalid structure")
            continue

        operations_valid = True

        for operation in loaded["operations"]:
            if not validate_operation_structure(operation):
                operations_valid = False

                operation_name = operation.get("title", "<unknown operation>")
                err_list.append(
                    f"Operation: {operation_name} has invalid structure"
                )

        if operations_valid:
            loaded_json.append(loaded)

    return loaded_json, err_list
