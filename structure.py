# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TypedDict, NotRequired, Literal, Union
from dataclasses import dataclass

class OperationDict(TypedDict):
    title: str
    program: str
    args: list[str]
    handler: str
    expected: NotRequired[str] # Do wywalenia po MVP


class ModeDict(TypedDict):
    name: str
    description: str
    operations: list[OperationDict]


@dataclass
class Operation:
    title: str
    program: str
    args: list[str]


@dataclass
class OperationResult:
    stdout: str
    stderr: str
    returncode: int


@dataclass
class HandlerResult:
    success: bool
    actual: str | int
    expected: str | int | None


def create_operation(operation_data: OperationDict) -> Operation:
    operation = Operation(
    operation_data["title"],
    operation_data["program"],
    operation_data["args"]
    )
    return operation

type OperationSuccess = tuple[Literal[True], HandlerResult]
type OperationFailure = tuple[Literal[False], Exception]
type OperationOutcome = Union[OperationSuccess, OperationFailure]
