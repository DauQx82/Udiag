# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from importlib import import_module

import pytest

from handlers.contains import ContainsHandler
from handlers.empty import EmptyHandler
from handlers.equals import EqualsHandler
from structure import HandlerResult


# `pass` is a Python keyword, so importing handlers.pass with a normal
# `from handlers.pass import PassHandler` statement is not valid syntax.
PassHandler = import_module("handlers.pass").PassHandler


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ("running", True),
        ("", True),
        (0, True),
        (7, True),
        (-1, True),
        (True, False),
        (False, False),
        (None, False),
        ({}, False),
        ([], False),
        (1.5, False),
    ],
)
def test_equals_validate_config(
    config: object,
    expected: bool,
) -> None:
    assert EqualsHandler.validate_config(config) is expected


def test_equals_evaluate_string_success() -> None:
    result = EqualsHandler("running\n", "running").evaluate()

    assert result == HandlerResult(
        success=True,
        actual="running",
        expected="running",
    )


def test_equals_evaluate_string_failure() -> None:
    result = EqualsHandler("degraded\n", "running").evaluate()

    assert result == HandlerResult(
        success=False,
        actual="degraded",
        expected="running",
    )


def test_equals_removes_only_line_endings() -> None:
    result = EqualsHandler("  running  \r\n", "  running  ").evaluate()

    assert result.success is True
    assert result.actual == "  running  "
    assert result.expected == "  running  "


@pytest.mark.parametrize(
    ("actual", "expected", "success"),
    [
        (0, 0, True),
        (1, 0, False),
        (7, 7, True),
        (-1, 0, False),
    ],
)
def test_equals_evaluate_returncode(
    actual: int,
    expected: int,
    success: bool,
) -> None:
    result = EqualsHandler(actual, expected).evaluate()

    assert result.success is success
    assert result.actual == actual
    assert result.expected == expected


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ("running", True),
        ("", True),
        (0, False),
        (True, False),
        (None, False),
        ({}, False),
        ([], False),
    ],
)
def test_contains_validate_config(
    config: object,
    expected: bool,
) -> None:
    assert ContainsHandler.validate_config(config) is expected


def test_contains_evaluate_success() -> None:
    result = ContainsHandler(
        "system is active and running\n",
        "running",
    ).evaluate()

    assert result.success is True
    assert result.actual == "system is active and running\n"
    assert result.expected == "running"


def test_contains_evaluate_failure() -> None:
    result = ContainsHandler(
        "system is degraded\n",
        "running",
    ).evaluate()

    assert result.success is False
    assert result.actual == "system is degraded\n"
    assert result.expected == "running"


def test_contains_rejects_integer_actual_during_evaluation() -> None:
    result = ContainsHandler(0, "0").evaluate()

    assert result.success is False
    assert result.actual == 0
    assert result.expected == "0"


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (True, True),
        (False, False),
        ("", False),
        (0, False),
        (None, False),
        ({}, False),
        ([], False),
    ],
)
def test_empty_validate_config(
    config: object,
    expected: bool,
) -> None:
    assert EmptyHandler.validate_config(config) is expected


@pytest.mark.parametrize(
    "actual",
    [
        "",
        "\n",
        "\r\n",
    ],
)
def test_empty_evaluate_success(actual: str) -> None:
    result = EmptyHandler(actual, True).evaluate()

    assert result.success is True
    assert result.actual == ""
    assert result.expected == ""


@pytest.mark.parametrize(
    "actual",
    [
        " ",
        "error",
        "error\n",
    ],
)
def test_empty_evaluate_failure(actual: str) -> None:
    result = EmptyHandler(actual, True).evaluate()

    assert result.success is False
    assert result.expected == ""


def test_empty_evaluate_integer_is_failure() -> None:
    result = EmptyHandler(0, True).evaluate()

    assert result.success is False
    assert result.actual == 0
    assert result.expected == ""


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (True, True),
        (False, False),
        ("", False),
        (0, False),
        (None, False),
        ({}, False),
        ([], False),
    ],
)
def test_pass_validate_config(
    config: object,
    expected: bool,
) -> None:
    assert PassHandler.validate_config(config) is expected


@pytest.mark.parametrize(
    "actual",
    [
        "",
        "Linux host\n",
        "  output with spaces  \n",
        0,
        7,
    ],
)
def test_pass_always_succeeds_and_preserves_actual(
    actual: str | int,
) -> None:
    result = PassHandler(actual, True).evaluate()

    assert result.success is True
    assert result.actual == actual
    assert result.expected is None
