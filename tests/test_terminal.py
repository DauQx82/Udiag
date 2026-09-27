# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from structure import (
    CheckResult,
    EvaluatedOperation,
    HandlerResult,
    OperationExecutionError,
    OperationOutcome,
    OperationResult,
    ValidatedOperation,
    SkippedOperation
)
from terminal import operation_status, present_list


def make_operation() -> ValidatedOperation:
    return {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "checks": [
            {
                "source": "stdout",
                "handler": "equals",
                "config": "running",
            }
        ],
    }


def make_evaluated_operation(
    success: bool,
    actual: str | int,
    expected: str | int | None,
) -> EvaluatedOperation:
    return EvaluatedOperation(
        process_result=OperationResult(
            stdout="",
            stderr="",
            returncode=0,
        ),
        check_results=[
            CheckResult(
                source="stdout",
                handler="equals",
                result=HandlerResult(
                    success=success,
                    actual=actual,
                    expected=expected,
                ),
            )
        ],
    )


@pytest.mark.parametrize(
    ("result", "expected_status"),
    [
        (
            make_evaluated_operation(
                True,
                "running",
                "running",
            ),
            "OK",
        ),
        (
            make_evaluated_operation(
                False,
                "degraded",
                "running",
            ),
            "FAIL",
        ),
        (
            OperationExecutionError(
                FileNotFoundError("program not found"),
            ),
            "ERROR",
        ),
    ],
)
def test_operation_status(
    result: OperationOutcome,
    expected_status: str,
) -> None:
    assert operation_status(result) == expected_status


def test_present_list_compact_ok(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation = make_operation()

    result = make_evaluated_operation(
        True,
        "running",
        "running",
    )

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "SUCCESS" in output
    assert "System state" in output
    assert "Actual value" not in output
    assert "Expected" not in output


def test_present_list_detailed_ok(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation = make_operation()

    result = make_evaluated_operation(
        True,
        "running",
        "running",
    )

    present_list(
        1,
        operation,
        result,
        with_details=True,
    )

    output = capsys.readouterr().out

    assert "SUCCESS" in output
    assert "System state" in output
    assert "stdout / equals" in output
    assert "Actual value:" in output
    assert "running" in output
    assert "Expected:" in output


def test_present_list_expands_only_failed_checks(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation = make_operation()

    result = EvaluatedOperation(
        process_result=OperationResult(
            stdout="running\n",
            stderr="",
            returncode=1,
        ),
        check_results=[
            CheckResult(
                source="stdout",
                handler="equals",
                result=HandlerResult(
                    success=True,
                    actual="running",
                    expected="running",
                ),
            ),
            CheckResult(
                source="returncode",
                handler="equals",
                result=HandlerResult(
                    success=False,
                    actual=1,
                    expected=0,
                ),
            ),
        ],
    )

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "FAILURE" in output
    assert "returncode / equals" in output
    assert "Actual value:" in output
    assert "1" in output
    assert "Expected:" in output

    assert "stdout / equals" not in output


def test_present_list_expands_error_without_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation = make_operation()

    result = OperationExecutionError(
        FileNotFoundError("command not found"),
    )

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "ERROR" in output
    assert "System state" in output
    assert "Exception:" in output
    assert "command not found" in output

def test_operation_status_skip() -> None:
    result = SkippedOperation("condition not met")

    assert operation_status(result) == "SKIP"


def test_present_list_skip(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation = make_operation()
    result = SkippedOperation("condition not met")

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "SKIP" in output
    assert "Reason:" in output
    assert "condition not met" in output