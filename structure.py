# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TypedDict, Literal
from dataclasses import dataclass

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


class ModeSkeleton(TypedDict):
    name: str
    description: str
    operations: list[dict[str, object]]


class OperationSkeleton(TypedDict):
    title: str
    program: str
    args: list[str]
    checks: dict[str, object]

type CheckSource = Literal["stdout", "stderr", "returncode"]

class CheckSkeleton(TypedDict):
    source: CheckSource
    handler: str
    config: object


class ValidatedOperation(TypedDict):
    title: str
    program: str
    args: list[str]
    checks: list[CheckSkeleton]


class ValidatedMode(TypedDict):
    name: str
    description: str
    operations: list[ValidatedOperation]


@dataclass
class CheckResult:
    source: CheckSource
    handler: str
    result: HandlerResult


@dataclass
class EvaluatedOperation:
    process_result: OperationResult
    check_results: list[CheckResult]

    @property
    def success(self) -> bool:
        return all(
            check.result.success
            for check in self.check_results
        )


@dataclass
class OperationExecutionError:
    error: Exception

@dataclass
class SkippedOperation:
    reason: str


type OperationOutcome = (
    EvaluatedOperation | OperationExecutionError | SkippedOperation
)

def create_operation(operation_data: ValidatedOperation) -> Operation:
    operation = Operation(
    operation_data["title"],
    operation_data["program"],
    operation_data["args"]
    )
    return operation