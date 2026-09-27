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
    CheckResult,
    EvaluatedOperation,
    OperationExecutionError,
    OperationOutcome,
    OperationResult,
    Operation,
    ValidatedMode,
    ValidatedOperation,
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
    tuple[int, ValidatedOperation, OperationOutcome]
    ] = []

    def raise_execution_error(operation) -> None:
        raise error

    def capture_result(
        i: int,
        operation_data: ValidatedOperation,
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
    assert isinstance(outcome, OperationExecutionError)
    assert outcome.error is error


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
                    "checks": [
                        {
                            "source": "stdout",
                            "handler": "equals",
                            "config": "ok",
                        }
                    ],
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

    modes: list[ValidatedMode] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "checks": [
                        {
                            "source": "stdout",
                            "handler": "equals",
                            "config": "ok",
                        }
                    ],
                }
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    presented: list[
        tuple[int, ValidatedOperation, OperationOutcome]
    ] = []

    def successful_execution(operation) -> OperationResult:
        return OperationResult(
            stdout="ok\n",
            stderr="",
            returncode=0,
        )

    def capture_result(
        i: int,
        operation_data: ValidatedOperation,
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

    assert isinstance(outcome, EvaluatedOperation)
    assert outcome.success is True

    assert len(outcome.check_results) == 1

    check_result = outcome.check_results[0]

    assert check_result.source == "stdout"
    assert check_result.handler == "equals"

    handler_result = check_result.result

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

    modes: list[ValidatedMode] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Test operation",
                    "program": "test-program",
                    "args": [],
                    "checks": [
                        {
                            "source": "stdout",
                            "handler": "equals",
                            "config": "ok",
                        }
                    ],
                }
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    presented: list[
        tuple[int, ValidatedOperation, OperationOutcome]
    ] = []

    def nonzero_execution(operation: Operation) -> OperationResult:
        return OperationResult(
            stdout="ok\n",
            stderr="warning\n",
            returncode=7,
        )

    def capture_result(
        i: int,
        operation_data: ValidatedOperation,
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

    assert isinstance(outcome, EvaluatedOperation)
    assert outcome.success is True

    check_result = outcome.check_results[0]

    assert check_result.result.success is True
    assert check_result.result.actual == "ok"
    assert check_result.result.expected == "ok"


def test_main_continues_after_execution_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="run",
        mode="test",
        details=False,
    )

    modes: list[ValidatedMode] = [
        {
            "name": "test",
            "description": "Test mode",
            "operations": [
                {
                    "title": "Broken operation",
                    "program": "broken-program",
                    "args": [],

                    "checks": [
                        {
                            "source": "stdout",
                            "handler": "equals",
                            "config": "ok",
                        }
                    ],
                },
                {
                    "title": "Working operation",
                    "program": "working-program",
                    "args": [],

                    "checks": [
                        {
                            "source": "stdout",
                            "handler": "equals",
                            "config": "ok",
                        }
                    ]
                },
            ],
        }
    ]

    registry: dict[str, type[BaseHandler]] = {
        "equals": EqualsHandler
    }

    executed: list[str] = []
    presented: list[
        tuple[int, ValidatedOperation, OperationOutcome]
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
        operation_data: ValidatedOperation,
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

    assert isinstance(first_outcome, OperationExecutionError)
    assert isinstance(first_outcome.error, FileNotFoundError)

    assert isinstance(second_outcome, EvaluatedOperation)
    assert second_outcome.success is True


def test_parser_list() -> None:
    parser = udiag.build_parser([])

    args = parser.parse_args(["list"])

    assert args.command == "list"
    assert args.mode_errors is False


def test_parser_about() -> None:
    parser = udiag.build_parser([])

    args = parser.parse_args(["about"])

    assert args.command == "about"
    assert args.mode_errors is False


def test_print_mode_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    modes: list[ValidatedMode] = [
        {
            "name": "base",
            "description": "Basic system diagnostic",
            "operations": [],
        },
        {
            "name": "system",
            "description": "System diagnostic",
            "operations": [],
        },
    ]

    udiag.print_mode_list(modes)

    output = capsys.readouterr().out

    assert "Available diagnostic modes:" in output
    assert "base" in output
    assert "Basic system diagnostic" in output
    assert "system" in output
    assert "System diagnostic" in output


def test_print_mode_list_empty(
    capsys: pytest.CaptureFixture[str],
) -> None:
    udiag.print_mode_list([])

    output = capsys.readouterr().out

    assert "No diagnostic modes available." in output


def test_print_about(
    capsys: pytest.CaptureFixture[str],
) -> None:
    udiag.print_about()

    output = capsys.readouterr().out

    assert "Udiag" in output
    assert "Declarative diagnostic scenario runner" in output
    assert "GPL-3.0-or-later" in output


def test_main_handles_list_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="list",
    )

    modes: list[ValidatedMode] = []

    called = False

    def capture_list(
        valid_modes: list[ValidatedMode],
    ) -> None:
        nonlocal called
        called = True
        assert valid_modes is modes

    monkeypatch.setattr(
        udiag,
        "print_mode_list",
        capture_list,
    )

    udiag.main(args, {}, modes)

    assert called is True


def test_main_handles_about_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = Namespace(
        mode_errors=False,
        command="about",
    )

    called = False

    def capture_about() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(
        udiag,
        "print_about",
        capture_about,
    )

    udiag.main(args, {}, [])

    assert called is True
