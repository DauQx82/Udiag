# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from structure import HandlerResult, OperationDict, OperationOutcome
from terminal import operation_status, present_list


@pytest.mark.parametrize(
    ("result", "expected_status"),
    [
        (
            (True, HandlerResult(True, "running", "running")),
            "OK",
        ),
        (
            (True, HandlerResult(False, "degraded", "running")),
            "FAIL",
        ),
        (
            (False, FileNotFoundError("program not found")),
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
    operation: OperationDict = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "handler": "equals",
        "expected": "running",
    }

    result: OperationOutcome = (
        True,
        HandlerResult(True, "running", "running"),
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
    operation: OperationDict = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "handler": "equals",
        "expected": "running",
    }

    result: OperationOutcome = (
        True,
        HandlerResult(True, "running", "running"),
    )

    present_list(1, operation, result, with_details=True)

    output = capsys.readouterr().out

    assert "SUCCESS" in output
    assert "System state" in output
    assert "Actual value:" in output
    assert "running" in output
    assert "Expected:" in output


def test_present_list_expands_fail_without_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation: OperationDict = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "handler": "equals",
        "expected": "running",
    }

    result: OperationOutcome = (
        True,
        HandlerResult(False, "degraded", "running"),
    )

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "FAILURE" in output
    assert "Actual value:" in output
    assert "degraded" in output
    assert "Expected:" in output
    assert "running" in output


def test_present_list_expands_error_without_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    operation: OperationDict = {
        "title": "SMART check",
        "program": "smartctl",
        "args": [],
        "handler": "equals",
        "expected": "",
    }

    error = FileNotFoundError("command not found")
    result: OperationOutcome = (False, error)

    present_list(1, operation, result)

    output = capsys.readouterr().out

    assert "ERROR" in output
    assert "SMART check" in output
    assert "Exception:" in output
    assert "command not found" in output