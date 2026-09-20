# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from argparse import Namespace
import pytest

import udiag
from structure import OperationDict, OperationOutcome
from handlers.handler import BaseHandler
from handlers.equals import EqualsHandler
from structure import (
    ModeDict,
    OperationDict,
    OperationOutcome,
    OperationResult,
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

    def capture_result(i, operation_data, outcome) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        raise_execution_error,
    )
    monkeypatch.setattr(
        udiag,
        "present_terminal",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode: None,
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
        lambda mode: None,
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
    ) -> None:
        presented.append((i, operation_data, outcome))

    monkeypatch.setattr(
        udiag,
        "execute_operation",
        successful_execution,
    )
    monkeypatch.setattr(
        udiag,
        "present_terminal",
        capture_result,
    )
    monkeypatch.setattr(
        udiag,
        "terminal_title",
        lambda mode: None,
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
