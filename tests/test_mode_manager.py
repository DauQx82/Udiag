# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from typing import cast

import pytest

from handlers.handler import BaseHandler
from mode_manager import (
    CheckSkeleton,
    find_mode_files,
    prepare_modes,
    validate_checks,
    validate_checks_structure,
    validate_mode_structure,
    validate_operation_structure,
)


class AcceptHandler:
    """Minimal test double that accepts every configuration."""

    @classmethod
    def validate_config(cls, config: object) -> bool:
        return True


class StringHandler:
    """Minimal test double that accepts only string configuration."""

    @classmethod
    def validate_config(cls, config: object) -> bool:
        return isinstance(config, str)


def build_registry() -> dict[str, type[BaseHandler]]:
    """Builds a small handler registry used by mode-manager tests."""
    return {
        "accept": cast(type[BaseHandler], AcceptHandler),
        "string": cast(type[BaseHandler], StringHandler),
    }


def write_mode(
    tmp_path: Path,
    filename: str,
    data: object,
) -> Path:
    """Writes JSON test data and returns its path."""
    mode_file = tmp_path / filename
    mode_file.write_text(
        json.dumps(data),
        encoding="utf-8",
    )
    return mode_file


def test_find_mode_files_returns_modes() -> None:
    mode_files = find_mode_files()
    assert mode_files != []


@pytest.mark.parametrize(
    "mode",
    [
        {
            "description": "Missing name",
            "operations": [{}],
        },
        {
            "name": 42,
            "description": "Name is not a string",
            "operations": [{}],
        },
        {
            "name": "missing-description",
            "operations": [{}],
        },
        {
            "name": "missing-operations",
            "description": "Operations field is missing",
        },
        {
            "name": "operations-not-list",
            "description": "Operations is an object",
            "operations": {},
        },
        {
            "name": "operation-not-object",
            "description": "Operation is a string",
            "operations": ["not-an-object"],
        },
        {
            "name": "empty-operations",
            "description": "Operations list is empty",
            "operations": [],
        },
    ],
)
def test_validate_mode_structure_rejects_invalid_modes(
    mode: dict,
) -> None:
    result = validate_mode_structure(mode)

    assert result[0] is False
    assert result[1]


@pytest.mark.parametrize(
    "mode",
    [
        {
            "name": "example",
            "description": "Example",
            "operations": [{}],
        },
        {
            "name": "test-mode",
            "description": "Testing mode",
            "operations": [
                {
                    "some": "raw operation",
                }
            ],
        },
    ],
)
def test_validate_mode_structure_returns_mode_skeleton(
    mode: dict,
) -> None:
    result = validate_mode_structure(mode)

    assert result[0] is True

    mode_skeleton = result[1]

    assert mode_skeleton["name"] == mode["name"]
    assert mode_skeleton["description"] == mode["description"]
    assert mode_skeleton["operations"] == mode["operations"]


@pytest.mark.parametrize(
    "operation",
    [
        # Missing title.
        {
            "program": "systemctl",
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Title is not str.
        {
            "title": 42,
            "program": "systemctl",
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Missing program.
        {
            "title": "System state",
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Program is not str.
        {
            "title": "System state",
            "program": 42,
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Program is empty.
        {
            "title": "System state",
            "program": "",
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Program contains only whitespace.
        {
            "title": "System state",
            "program": "   ",
            "args": ["is-system-running"],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Missing args.
        {
            "title": "System state",
            "program": "systemctl",
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Args is not list.
        {
            "title": "System state",
            "program": "systemctl",
            "args": "is-system-running",
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Args contains non-string value.
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running", 42],
            "checks": {
                "stdout": {
                    "accept": "running",
                }
            },
        },
        # Missing checks.
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running"],
        },
        # Checks is not dict.
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running"],
            "checks": [],
        },
        # Checks is empty.
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running"],
            "checks": {},
        },
    ],
)
def test_validate_operation_structure_rejects_invalid_operations(
    operation: dict,
) -> None:
    result = validate_operation_structure(operation)

    assert result[0] is False
    assert result[1]


def test_validate_operation_structure_returns_operation_skeleton() -> None:
    operation = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "checks": {
            "stdout": {
                "accept": "running",
            },
            "returncode": {
                "accept": 0,
            },
        },
    }

    result = validate_operation_structure(operation)

    assert result[0] is True

    operation_skeleton = result[1]

    assert operation_skeleton["title"] == "System state"
    assert operation_skeleton["program"] == "systemctl"
    assert operation_skeleton["args"] == ["is-system-running"]
    assert operation_skeleton["checks"] == operation["checks"]


def test_validate_checks_structure_flattens_checks() -> None:
    operation = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "checks": {
            "stdout": {
                "accept": "running",
                "string": "run",
            },
            "stderr": {
                "accept": True,
            },
            "returncode": {
                "accept": 0,
            },
        },
    }

    operation_result = validate_operation_structure(operation)
    assert operation_result[0] is True

    checks_result = validate_checks_structure(operation_result[1])

    assert checks_result[0] is True
    assert checks_result[1] == [
        {
            "source": "stdout",
            "handler": "accept",
            "config": "running",
        },
        {
            "source": "stdout",
            "handler": "string",
            "config": "run",
        },
        {
            "source": "stderr",
            "handler": "accept",
            "config": True,
        },
        {
            "source": "returncode",
            "handler": "accept",
            "config": 0,
        },
    ]


@pytest.mark.parametrize(
    "checks",
    [
        {
            "unsupported-source": {
                "accept": True,
            }
        },
        {
            "stdout": "not-a-handler-map",
        },
        {
            "stdout": {},
        },
    ],
)
def test_validate_checks_structure_rejects_invalid_structure(
    checks: object,
) -> None:
    operation = {
        "title": "System state",
        "program": "systemctl",
        "args": ["is-system-running"],
        "checks": checks,
    }

    operation_result = validate_operation_structure(operation)

    # The operation-level validator only verifies that checks itself is a
    # non-empty dict. Nested check structure belongs to the next validator.
    assert operation_result[0] is True

    checks_result = validate_checks_structure(operation_result[1])

    assert checks_result[0] is False
    assert checks_result[1]


def test_validate_checks_accepts_known_handler_and_valid_config() -> None:
    checks: list[CheckSkeleton] = [
        {
            "source": "stdout",
            "handler": "string",
            "config": "running",
        }
    ]

    result = validate_checks(
        checks,
        build_registry(),
    )

    assert result == (True, checks)


def test_validate_checks_rejects_unknown_handler() -> None:
    checks: list[CheckSkeleton] = [
        {
            "source": "stdout",
            "handler": "does-not-exist",
            "config": "running",
        }
    ]

    result = validate_checks(
        checks,
        build_registry(),
    )

    assert result[0] is False
    assert "does-not-exist" in result[1]
    assert "stdout" in result[1]


def test_validate_checks_rejects_invalid_handler_config() -> None:
    checks: list[CheckSkeleton] = [
        {
            "source": "returncode",
            "handler": "string",
            "config": 0,
        }
    ]

    result = validate_checks(
        checks,
        build_registry(),
    )

    assert result[0] is False
    assert "string" in result[1]
    assert "returncode" in result[1]


def test_prepare_modes_accepts_valid_mode(
    tmp_path: Path,
) -> None:
    mode_file = write_mode(
        tmp_path,
        "valid.json",
        {
            "name": "base",
            "description": "Basic diagnostic",
            "operations": [
                {
                    "title": "System state",
                    "program": "systemctl",
                    "args": ["is-system-running"],
                    "checks": {
                        "stdout": {
                            "string": "running",
                        },
                        "returncode": {
                            "accept": 0,
                        },
                    },
                }
            ],
        },
    )

    valid_modes, errors = prepare_modes(
        [mode_file],
        build_registry(),
    )

    assert errors == []
    assert len(valid_modes) == 1

    mode = valid_modes[0]

    assert mode["name"] == "base"
    assert mode["description"] == "Basic diagnostic"
    assert len(mode["operations"]) == 1

    operation = mode["operations"][0]

    assert operation["title"] == "System state"
    assert operation["program"] == "systemctl"
    assert operation["args"] == ["is-system-running"]
    assert operation["checks"] == [
        {
            "source": "stdout",
            "handler": "string",
            "config": "running",
        },
        {
            "source": "returncode",
            "handler": "accept",
            "config": 0,
        },
    ]


def test_prepare_modes_skips_invalid_operation_and_keeps_valid_siblings(
    tmp_path: Path,
) -> None:
    mode_file = write_mode(
        tmp_path,
        "partial.json",
        {
            "name": "partial",
            "description": "Partial validity test",
            "operations": [
                {
                    "title": "First valid operation",
                    "program": "program-one",
                    "args": [],
                    "checks": {
                        "stdout": {
                            "accept": True,
                        }
                    },
                },
                {
                    "title": "Broken operation",
                    "program": "program-two",
                    "args": [],
                    "checks": {
                        "stdout": {
                            "does-not-exist": True,
                        }
                    },
                },
                {
                    "title": "Second valid operation",
                    "program": "program-three",
                    "args": [],
                    "checks": {
                        "returncode": {
                            "accept": 0,
                        }
                    },
                },
            ],
        },
    )

    valid_modes, errors = prepare_modes(
        [mode_file],
        build_registry(),
    )

    assert len(valid_modes) == 1
    assert [
        operation["title"]
        for operation in valid_modes[0]["operations"]
    ] == [
        "First valid operation",
        "Second valid operation",
    ]

    assert len(errors) == 1
    assert "Broken operation" in errors[0]
    assert "does-not-exist" in errors[0]


def test_prepare_modes_rejects_mode_when_no_operation_is_valid(
    tmp_path: Path,
) -> None:
    mode_file = write_mode(
        tmp_path,
        "no_valid_operations.json",
        {
            "name": "broken",
            "description": "No valid operations",
            "operations": [
                {
                    "title": "Broken operation",
                    "program": "systemctl",
                    "args": [],
                    "checks": {
                        "stdout": {
                            "does-not-exist": True,
                        }
                    },
                }
            ],
        },
    )

    valid_modes, errors = prepare_modes(
        [mode_file],
        build_registry(),
    )

    assert valid_modes == []
    assert len(errors) == 2
    assert "Broken operation" in errors[0]
    assert "no valid operations" in errors[1]


def test_prepare_modes_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    mode_file = tmp_path / "invalid.json"
    mode_file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    valid_modes, errors = prepare_modes(
        [mode_file],
        build_registry(),
    )

    assert valid_modes == []
    assert len(errors) == 1
    assert "invalid JSON" in errors[0]


@pytest.mark.parametrize(
    "root_value",
    [
        None,
        42,
        True,
        "hello",
        [],
    ],
)
def test_prepare_modes_rejects_non_object_json_root(
    tmp_path: Path,
    root_value: object,
) -> None:
    mode_file = write_mode(
        tmp_path,
        "invalid_root.json",
        root_value,
    )

    valid_modes, errors = prepare_modes(
        [mode_file],
        build_registry(),
    )

    assert valid_modes == []
    assert len(errors) == 1
    assert "root JSON value must be an object" in errors[0]
