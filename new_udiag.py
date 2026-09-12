import os
import subprocess
import argparse
import sys
from dataclasses import dataclass

from mode_manager import prepare_modes

env_with_colors = os.environ.copy()
env_with_colors["SYSTEMD_COLORS"] = "1"

@dataclass
class Operation:
	id: str
	title: str
	mode: str
	program: str
	command: str

	stdout: str = ""
	stderr: str = ""
	returncode: int | None = None

def warning(errors: list[str]) -> None:
	if errors:
		print()
		print(f"{len(errors)} : Modes are not available")
		print("For details, run new_udiag.py --errors, -e")
		# FIXME new_udiag -> udiag, when migration time

def warning_details(errors: list[str]) -> None:
	if errors:
		print(f"{len(errors)} : Modes are not available")
		print("Details:" + "\n")

		for i, error in enumerate(errors, start=1):
			print(f"{i}. {error}" + "\n")
		return

	print("No errors.")

def create_operation(instruction: dict) -> Operation:
	operation = Operation(
	instruction["id"],
	instruction["title"],
	instruction["mode"],
	instruction["program"],
	instruction["command"]
	)
	return operation

def execute(operation: Operation) -> None:
	result = subprocess.run(operation.command,
							shell=True,
							capture_output=True,
							text=True,
							env=env_with_colors)

	operation.stdout = result.stdout
	operation.stderr = result.stderr
	operation.returncode = result.returncode

def main(args, correct_modes: list[dict], errors: list[str]) -> None:
	for mode in correct_modes:
		if getattr(args, mode["name"]):
			warning(errors)

			print(f"You choose: {mode['name']}")
			print()
			
			for instruction in mode["operations"]:
				print(f"Operation: {instruction['title']}")
				print(f"Command: {instruction['command']}")

				operation = create_operation(instruction)
				
				execute(operation)

				print(operation.stdout)
				print(operation.returncode)
				print()


# Parser init
parser = argparse.ArgumentParser(description="Udiag - Diagnostic system with JSON")

parser.add_argument("--errors", "-e", dest="mode_errors", action="store_true", help="Check modes errors")

correct_modes, errors = prepare_modes()
for mode in correct_modes:
	parser.add_argument(
		*mode["arguments"],
		dest=mode["name"],
		action="store_true",
		help=mode["description"]
	)

if __name__ == "__main__":
	args = parser.parse_args()

	if len(sys.argv) == 1:
		warning(errors)

		parser.print_help()

	if args.mode_errors:
		warning_details(errors)

	main(args, correct_modes, errors)
