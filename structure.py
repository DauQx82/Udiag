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

@dataclass
class OperationResult:
    stdout: str
    stderr: str
    returncode: int

@dataclass
class HandlerResult:
    success: bool
    actual: str
    expected: str| int | None

def create_operation(operation_data: OperationDict) -> Operation:
    operation = Operation(
    operation_data["title"],
    operation_data["program"],
    operation_data["args"]
    )
    return operation