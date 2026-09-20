# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from handlers.equals import EqualsHandler
from structure import OperationResult

def test_equals_handler():
    result_list = []

    operations = [
        {"expected": "equals"},
        {"expected": ""},
        {"expected": 42},
        {"expected": None},
        {"expected": {}},
        {"expected": []}
        ]

    for operation in operations:
        result = EqualsHandler.validate_config(operation)

        if result:
            result_list.append(operation)

    assert len(result_list) == 2
    assert {"expected": "equals"} in result_list
    assert {"expected": ""} in result_list
    assert {"expected": 42} not in result_list
    assert {"expected": None} not in result_list
    assert {"expected": {}} not in result_list
    assert {"expected": []} not in result_list


def test_equals_handler_evaluate_success() -> None:
    operation_result = OperationResult(
        stdout="running\n",
        stderr="",
        returncode=0,
    )

    handler = EqualsHandler(operation_result, "running")
    result = handler.evaluate()

    assert result.success is True
    assert result.actual == "running"
    assert result.expected == "running"


def test_equals_handler_evaluate_failure() -> None:
    operation_result = OperationResult(
        stdout="degraded\n",
        stderr="",
        returncode=0,
    )

    handler = EqualsHandler(operation_result, "running")
    result = handler.evaluate()

    assert result.success is False
    assert result.actual == "degraded"
    assert result.expected == "running"


def test_equals_handler_removes_only_line_endings() -> None:
    operation_result = OperationResult(
        stdout="  running  \n",
        stderr="",
        returncode=0,
    )

    handler = EqualsHandler(operation_result, "  running  ")
    result = handler.evaluate()

    assert result.success is True
    assert result.actual == "  running  "


def test_equals_handler_accepts_empty_stdout() -> None:
    operation_result = OperationResult(
        stdout="",
        stderr="",
        returncode=0,
    )

    handler = EqualsHandler(operation_result, "")
    result = handler.evaluate()

    assert result.success is True
    assert result.actual == ""
    assert result.expected == ""