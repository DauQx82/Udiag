from getpass import getuser
from socket import gethostname
from datetime import datetime
from structure import ModeDict, OperationDict, Operation

def terminal_title(mode: ModeDict) -> None:
	print(f"=== {mode["description"]} ===")
	print(f"# Runtime: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
	print(f"# User: {getuser()} | Device: {gethostname()}")

def present_terminal(i: int,
					 instruction: OperationDict,
					 operation: Operation) -> None:
	"""Preparing a report""" # TODO Full docstring.

	print(f"	[{i}] {instruction['title']}\n")
	print(f"Command: {instruction['command']}\n")

	print(f"{operation.stdout}")
	print(f"Returncode: {operation.returncode}")
	print()
