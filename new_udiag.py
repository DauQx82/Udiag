import os
import subprocess
import argparse
import sys

from mode_manager import prepare_modes
# Parser init
parser = argparse.ArgumentParser(description="Udiag - Diagnostic system with JSON")

modes, errors = prepare_modes()
for mode in modes:
	parser.add_argument(
		*mode["arguments"],
		dest=mode["name"],
		action="store_true",
		help=mode["description"]
	)

if __name__ == "__main__":
	args = parser.parse_args()

	if len(sys.argv) == 1:
		parser.print_help()

	for mode in modes:
		if getattr(args, mode["name"]):
			print(f"You choose: {mode['name']}")
			print()

			for operation in mode["operations"]:
				print(f"Operation: {operation["title"]}")
				print(f"Command: {operation["command"]}")
				subprocess.run(operation["command"], shell=True)
				print()