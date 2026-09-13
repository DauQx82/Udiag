import os
import subprocess
import argparse
import sys

from mode_manager import prepare_modes
from structure import ModeDict, Operation, create_operation

from terminal import present_terminal, terminal_title

env_with_colors = os.environ.copy()
env_with_colors["SYSTEMD_COLORS"] = "1"

def prepare_args(mode: ModeDict) -> list[str]:
	"""Prepares a list of arguments for each specific mode."""
	args_list: list[str] = []

	args_list.extend(f"-{alias}" for alias in mode['aliases'])
	args_list.append(f"--{mode['name']}")

	return args_list

def build_parser(correct_modes: list[ModeDict]) -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Udiag - Diagnostic system with JSON"
	)

	parser.add_argument(
		"-e",
		"--errors",
		dest="mode_errors",
		action="store_true",
		help="Check modes errors"
	)

	for mode in correct_modes:
		parser.add_argument(
			*prepare_args(mode),
			dest=mode["name"],
			action="store_true",
			help=mode["description"]
		)

	return parser

def warning(errors: list[str]) -> None:
	if errors:
		print()
		print(f"{len(errors)} : Modes are not available")
		print("For details, run udiag.py -e, --errors" + "\n")

def warning_details(errors: list[str]) -> None:
	if errors:
		print(f"{len(errors)} : Modes are not available")
		print("Details:" + "\n")

		for i, error in enumerate(errors, start=1):
			print(f"{i}. {error}" + "\n")

		return

	print("No errors.")

def execute(operation: Operation) -> None:
	result = subprocess.run(operation.command,
							shell=True,
							capture_output=True,
							text=True,
							env=env_with_colors)

	operation.stdout = result.stdout
	operation.stderr = result.stderr
	operation.returncode = result.returncode

def main(args, correct_modes: list[ModeDict], errors: list[str]) -> None:
	for mode in correct_modes:
		if getattr(args, mode["name"]):
			warning(errors)
			print()

			terminal_title(mode)
			
			for i, instruction in enumerate(mode["operations"], start=1):
				operation = create_operation(instruction)
				
				execute(operation)

				present_terminal(i, instruction, operation)
			
			print("# End.")

if __name__ == "__main__":
	correct_modes, errors = prepare_modes()

	parser = build_parser(correct_modes)
	args = parser.parse_args()

	if len(sys.argv) == 1:
		warning(errors)
		parser.print_help()

	if args.mode_errors:
		warning_details(errors)

	main(args, correct_modes, errors)
