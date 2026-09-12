import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODE_DIR = BASE_DIR / "modes"

def scan_config() -> list[Path]:
	"""Scans path for modes. Returns Path obj."""
	return list(MODE_DIR.glob("*.json"))

def load_mode(file: Path) -> dict:
	"""Loading configuration details. Returns dict [json]"""
	with file.open("r", encoding="utf-8") as f:
		return json.load(f)

def validate_json(file: Path) -> bool:
	"""Return true if json has no errors"""
	try:
		load_mode(file)
	except json.JSONDecodeError:
		return False
	
	return True

def validate_mode_structure(mode: dict[str, object]) -> bool:
	"""Checks whether the dictionary contains the required diagnostic keys and whether their values ​​have the correct types."""

	expected_structure:dict = {
		"name": str,
		"description": str,
		"arguments": list, # list of str
		"operations": list # list of dict
	}

	for key, expected_type in expected_structure.items():
		if key not in mode:
			return False
		
		if not isinstance(mode[key], expected_type):
			return False

	return True

def prepare_modes() -> tuple[list[dict], list[str]]:
	"""Checks the structure of the JSON file."""
	modes = scan_config()
	loaded_json:list[dict] = []
	err_list:list[str] = []

	for mode in modes:
		if (validate_json(mode)):
			loaded = load_mode(mode)
			if validate_mode_structure(loaded):
				loaded_json.append(loaded)
			else:
				err_list.append(f"Mode: {mode} has invalid structure")
		else:
			message: str = f"Mode: {mode} JSONDecodeError return Err" + "\n" + f"Check your {mode.name}"
			err_list.append(message)

	return loaded_json, err_list
