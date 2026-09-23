# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from argparse import Namespace
import pytest
import sys

import udiag
from handlers.handler import BaseHandler
from handlers.equals import EqualsHandler
from structure import (
    ModeDict,
    OperationDict,
    OperationOutcome,
    OperationResult,
    Operation,
)
# README!
# type: ignore[arg-type] ← I use this construct so that Pylance doesn't report a type error.
# This helps with further work because I can immediately see actual errors.

def test_get_mode_names_empty():
    assert udiag.get_mode_names([]) == []


def test_get_mode_names():
    modes = [
        {
            "name": "base",
            "description": "Base diagnostic",
            "operations": []
        },
        {
            "name": "system",
            "description": "System diagnostic",
            "operations": []
        }
    ]

    result = udiag.get_mode_names(modes) #type: ignore[arg-type]

    assert result == ["base", "system"]


def test_parser_run():
    modes = [
        {
            "name": "base",
            "description": "Base diagnostic",
            "operations": []
        }
    ]

    parser = udiag.build_parser(modes) #type: ignore[arg-type]
    args = parser.parse_args(["run", "base"])

    assert args.command == "run"
    assert args.mode == "base"
    assert args.mode_errors is False


def test_parser_show():
    modes = [
        {
            "name": "base",
            "description": "Base diagnostic",
            "operations": []
        }
    ]

    parser = udiag.build_parser(modes) #type: ignore[arg-type]
    args = parser.parse_args(["show", "base"])

    assert args.command == "show"
    assert args.mode == "base"


def test_parser_errors():
    parser = udiag.build_parser([])

    args = parser.parse_args(["--errors"])

    assert args.mode_errors is True


def test_parser_run_with_details():
    modes = [
        {
            "name": "base",
            "description": "Basic",
            "operations": [],
        }
    ]

    parser = udiag.build_parser(modes)  # type: ignore[arg-type]
    args = parser.parse_args(["run", "base", "--details"])

    assert args.details is True


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("program not found"),
        PermissionError("permission denied"),
        subprocess.TimeoutExpired(
            cmd=["test-program"],
            timeout=10,
        ),
    ],
)
def test_main_converts_execution_failure_to_error_outcome(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                }
            ],
        }
    ]

    presented: list[
    tuple[int, OperationDict, OperationOutcome]
    ] = []

    def raise_execution_error(operation) -> None:
        raise error

    def capture_result(
        i: int,
        operation_data: OperationDict,
        outcome: OperationOutcome,
        with_details: bool = False,
    ) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        raise_execution_error,
    )
    monkeypatch.setattr(
        udiag,
        "present_list",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode, with_details=False: None,
    )
    monkeypatch.setattr(
        udiag,
        "print_mode_warning",
        lambda: None,
    )

    udiag.main(args, {}, modes)  # type: ignore[arg-type]

    assert len(presented) == 1

    index, operation_data, outcome = presented[0]

    assert index == 1
    assert operation_data["title"] == "Test operation"
    assert outcome[0] is False
    assert outcome[1] is error


def test_main_does_not_hide_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                }
            ],
        }
    ]

    def raise_bug(operation) -> None:
        raise RuntimeError("programming bug")

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        raise_bug,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode, with_details=False: None
    )
    monkeypatch.setattr(
        udiag,
        "print_mode_warning",
        lambda: None,
    )

    with pytest.raises(RuntimeError, match="programming bug"):
        udiag.main(args, {}, modes)  # type: ignore[arg-type]


def test_main_converts_successful_execution_to_handler_outcome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes: list[ModeDict] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                }
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    presented: list[
        tuple[int, OperationDict, OperationOutcome]
    ] = []

    def successful_execution(operation) -> OperationResult:
        return OperationResult(
            stdout="ok\n",
            stderr="",
            returncode=0,
        )

    def capture_result(
        i: int,
        operation_data: OperationDict,
        outcome: OperationOutcome,
        with_details: bool = False,
    ) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        successful_execution,
    )
    monkeypatch.setattr(
        udiag,
        "present_list",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode, with_details=False: None
    )
    monkeypatch.setattr(
        udiag,
        "print_mode_warning",
        lambda: None,
    )

    udiag.main(args, registry, modes)

    assert len(presented) == 1

    index, operation_data, outcome = presented[0]

    assert index == 1
    assert operation_data["title"] == "Test operation"

    assert outcome[0] is True

    handler_result = outcome[1]

    assert handler_result.success is True
    assert handler_result.actual == "ok"
    assert handler_result.expected == "ok"


def test_execute_operation_preserves_complete_nonzero_result() -> None:
    operation = Operation(
        title="Test process result",
        program=sys.executable,
        args=[
            "-c",
            (
                "import sys; "
                "print('stdout-value'); "
                "print('stderr-value', file=sys.stderr); "
                "sys.exit(7)"
            ),
        ],
    )

    result = udiag.execute_operation(operation)

    assert result.stdout == "stdout-value\n"
    assert result.stderr == "stderr-value\n"
    assert result.returncode == 7


def test_main_treats_nonzero_returncode_as_normal_outcome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes: list[ModeDict] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                }
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    presented: list[
        tuple[int, OperationDict, OperationOutcome]
    ] = []

    def nonzero_execution(operation: Operation) -> OperationResult:
        return OperationResult(
            stdout="ok\n",
            stderr="warning\n",
            returncode=7,
        )

    def capture_result(
        i: int,
        operation_data: OperationDict,
        outcome: OperationOutcome,
        with_details: bool = False,
    ) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        nonzero_execution,
    )
    monkeypatch.setattr(
        udiag,
        "present_list",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode, with_details=False: None,
    )
    monkeypatch.setattr(
        udiag,
        "print_mode_warning",
        lambda: None,
    )

    udiag.main(args, registry, modes)

    assert len(presented) == 1

    outcome = presented[0][2]

    assert outcome[0] is True
    assert outcome[1].success is True
    assert outcome[1].actual == "ok"
    assert outcome[1].expected == "ok"


def test_main_continues_after_execution_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes: list[ModeDict] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Broken operation",
                    "program": "broken-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                },
                {
                    "title": "Working operation",
                    "program": "working-program",
                    "args": [],
                    "handler": "equals",
                    "expected": "ok",
                },
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    executed: list[str] = []
    presented: list[
        tuple[int, OperationDict, OperationOutcome]
    ] = []

    def execute(operation: Operation) -> OperationResult:
        executed.append(operation.title)

        if operation.title == "Broken operation":
            raise FileNotFoundError("program not found")

        return OperationResult(
            stdout="ok\n",
            stderr="",
            returncode=0,
        )

    def capture_result(
        i: int,
        operation_data: OperationDict,
        outcome: OperationOutcome,
        with_details: bool = False,
    ) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        execute,
    )
    monkeypatch.setattr(
        udiag,
        "present_list",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode, with_details=False: None,
    )
    monkeypatch.setattr(
        udiag,
        "print_mode_warning",
        lambda: None,
    )

    udiag.main(args, registry, modes)

    assert executed == [
        "Broken operation",
        "Working operation",
    ]

    assert len(presented) == 2

    first_outcome = presented[0][2]
    second_outcome = presented[1][2]

    assert first_outcome[0] is False
    assert isinstance(first_outcome[1], FileNotFoundError)

    assert second_outcome[0] is True
    assert second_outcome[1].success is True
