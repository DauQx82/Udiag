from typing import TypedDict, NotRequired
from dataclasses import dataclass

class OperationDict(TypedDict):
	title: str
	program: str
	args: list[str]
	handler: str
	expected: NotRequired[str]

class ModeDict(TypedDict):
	name: str
	description: str
	operations: list[OperationDict]

@dataclass
class Operation:
	title: str
	program: str
	args: list[str]

	stdout: str = ""
	stderr: str = ""
	returncode: int | None = None

def create_operation(instruction: OperationDict) -> Operation:
	operation = Operation(
	instruction["title"],
	instruction["program"],
	instruction["args"]
	)
	return operation