"""
	For creating or editing mode
"""

"""
file
 ├── name
 ├── scope
 ├── description
 ├── arguments
 └── operations
      ├── id
      ├── title
      ├── mode
      ├── program
      ├── command
      └── expected
           ├── type
           └── value
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
USER_MODES_DIR = CONFIG_DIR / "user"

def scan_config() -> tuple[list[Path | None], list[Path | None]]:
	"""
		Used: pathlib: .glob()

		Returns: tuple paths to system modes, paths to user modes
	"""
	system_modes = CONFIG_DIR.glob("*.json")
	user_modes = USER_MODES_DIR.glob("*.json")

	return list(system_modes), list(user_modes)

def load_mode(file: Path) -> dict:
	"""
		Used: json.load()

		Returns: dict [json]
	"""
	with file.open("r", encoding="utf-8") as f:
		return json.load(f)


# Test
y, x = scan_config()

for item in y:
	print(item)

print("##############")

for item in x:
	print(item)