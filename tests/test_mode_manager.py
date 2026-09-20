# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import json
from pathlib import Path
# README!
# type: ignore[arg-type] ← I use this construct so that Pylance doesn't report a type error.
# This helps with further work because I can immediately see actual errors.

from mode_manager import (find_mode_files,
                          validate_mode_structure,
                          validate_operation_structure,
                          prepare_modes)

from handlers.equals import EqualsHandler


def test_prepare_modes_accepts_valid_handler_config(
    tmp_path: Path,
) -> None:
    mode_file = tmp_path / "valid.json"
    mode_file.write_text(
        json.dumps(
            {
                "name": "base",
                "description": "Basic diagnostic",
                "operations": [
                    {
                        "title": "System state",
                        "program": "systemctl",
                        "args": ["is-system-running"],
                        "handler": "equals",
                        "expected": "running",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = {
        "equals": EqualsHandler,
    }

    valid_modes, errors = prepare_modes(
        [mode_file],
        registry,
    )

    assert len(valid_modes) == 1
    assert valid_modes[0]["name"] == "base"
    assert errors == []


def test_prepare_modes_rejects_unknown_handler(
    tmp_path: Path,
) -> None:
    mode_file = tmp_path / "unknown_handler.json"
    mode_file.write_text(
        json.dumps(
            {
                "name": "base",
                "description": "Basic diagnostic",
                "operations": [
                    {
                        "title": "System state",
                        "program": "systemctl",
                        "args": ["is-system-running"],
                        "handler": "does-not-exist",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = {
        "equals": EqualsHandler,
    }

    valid_modes, errors = prepare_modes(
        [mode_file],
        registry,
    )

    assert valid_modes == []
    assert len(errors) == 1
    assert "failed handler validation" in errors[0]


def test_prepare_modes_rejects_invalid_handler_config(
    tmp_path: Path,
) -> None:
    mode_file = tmp_path / "invalid_config.json"
    mode_file.write_text(
        json.dumps(
            {
                "name": "base",
                "description": "Basic diagnostic",
                "operations": [
                    {
                        "title": "System state",
                        "program": "systemctl",
                        "args": ["is-system-running"],
                        "handler": "equals",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = {
        "equals": EqualsHandler,
    }

    valid_modes, errors = prepare_modes(
        [mode_file],
        registry,
    )

    assert valid_modes == []
    assert len(errors) == 1
    assert "failed handler validation" in errors[0]


def test_prepare_modes_does_not_validate_handler_after_structure_failure(
    tmp_path: Path,
) -> None:
    mode_file = tmp_path / "invalid_structure.json"
    mode_file.write_text(
        json.dumps(
            {
                "name": "base",
                "description": "Basic diagnostic",
                "operations": [
                    {
                        "title": "Broken operation",
                        "program": "systemctl",
                        "args": ["is-system-running"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = {
        "equals": EqualsHandler,
    }

    valid_modes, errors = prepare_modes(
        [mode_file],
        registry,
    )

    assert valid_modes == []
    assert len(errors) == 1
    assert "invalid structure" in errors[0]

def test_scan_config():
    test_list = find_mode_files()
    assert test_list != []

@pytest.mark.parametrize(
        "mode",
        [
            # No name
            {
                "description":"Missing name",
                "operations":[]
            },
            # mode_name_is_not_str
            {
                "name":42,
                "description":"Name is not a string",
                "operations":[]
            },
            # no_description
            {
                "name":"missing-description",
                "operations":[]
            },
            # no_operations
            {
                "name":"missing-operations",
                "description":"Operations field is missing"
            },
            # operations_is_not_list
            {
                "name":"operations-not-list",
                "description":"Operations is an object",
                "operations":{}
            },
            # operations_is_not_object
            {
                "name":"operation-not-object",
                "description":"Operation is a string",
                "operations":["not-an-object"]
            }
        ]
)
def test_validate_mode_structure(mode):
    assert validate_mode_structure(mode) is False #type: ignore[arg-type]

@pytest.mark.parametrize(
    "operation",
    [
        # Missing title
        {
            "program": "systemctl",
            "args": ["is-system-running"],
            "handler": "equals",
            "expected": "running"
        },

        # Title is not str
        {
            "title": 42,
            "program": "systemctl",
            "args": ["is-system-running"],
            "handler": "equals",
            "expected": "running"
        },

        # Missing program
        {
            "title": "System state",
            "args": ["is-system-running"],
            "handler": "equals",
            "expected": "running"
        },

        # Program is not str
        {
            "title": "System state",
            "program": 42,
            "args": ["is-system-running"],
            "handler": "equals",
            "expected": "running"
        },

        # Missing args
        {
            "title": "System state",
            "program": "systemctl",
            "handler": "equals",
            "expected": "running"
        },

        # Args is not list
        {
            "title": "System state",
            "program": "systemctl",
            "args": "is-system-running",
            "handler": "equals",
            "expected": "running"
        },

        # Args contains non-string
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running", 42],
            "handler": "equals",
            "expected": "running"
        },

        # Missing handler
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running"],
            "expected": "running"
        },

        # Handler is not str
        {
            "title": "System state",
            "program": "systemctl",
            "args": ["is-system-running"],
            "handler": 42,
            "expected": "running"
        }
    ]
)
def test_invalid_operations(operation):
    assert validate_operation_structure(operation) is False  # type: ignore[arg-type]

@pytest.mark.parametrize(
        "mode",
        [{
            "name": "example",
            "description": "example",
            "operations": [{}]
        },
        {
            "name": "test-mode",
            "description": "Testing mode",
            "operations": []
        }]
        )
def test_mode_is_valid(mode):
    assert validate_mode_structure(mode) is True

@pytest.mark.parametrize(
        "operation",
        [
            {
                "title": "System information",
                "program": "hostnamectl",
                "args": [],
                
                "handler": "information"
            },

            {
                "title": "Kernel information",
                "program": "uname",
                "args": ["-a"],

                "handler": "information"
            },

            {
                "title": "System state",
                "program": "systemctl",
                "args": ["is-system-running"],

                "handler": "equals",
                "expected": "running"
            },

            {
                "title": "Failed system services",
                "program": "systemctl",
                "args": ["--failed", "--no-pager"],

                "handler": "equals",
                "expected": "0 loaded units listed"
            },

            {
                "title": "Package audit",
                "program": "dpkg",
                "args": ["--audit"],

                "handler": "empty"
            },
            {
                "title": "test - ls",
                "program": "ls",
                "args": [],

                "handler": "information"
            }
        ]
)
def test_valid_operations(operation):
    assert validate_operation_structure(operation)

def test_prepare_modes(tmp_path):
    test_modes = [
        {
            "name": "valid_test",
            "description": "Valid test",
            "operations": [
                {
                    "title": "System state",
                    "program": "systemctl",
                    "args": ["is-system-running"],
                    "handler": "equals",
                    "expected": "running"
                }
            ]
        },
        {
            "name": "valid_test_2_empty", 
            "description": "",
            "operations": [
                {
                    "title": "",
                    "program": "",
                    "args": [],
                    "handler": "equals",
                    "expected": ""
                }
            ]
        },
        {
            "name": "invalid_test_1",
            "description": "No operations"
        },
        {
            "name": "invalid_test_2_no_description",
            "operations": [
                {
                    "title": "System state",
                    "program": "systemctl",
                    "args": ["is-system-running"],
                    "handler": "equals",
                    "expected": "running"
                }
            ]
        },
        {
            "name": "invalid_test_3",
            "description": "Broken operations",
            "operations": [
                {
                    "title": "System state",
                    "handler": "equals",
                    "expected": "running"
                }
            ]
        },
        {
            "name": "invalid_test_4", 
            "description": "",
            "operations": [
                {
                    "title": "",
                    "program": "",
                    "args": [],
                    "handler": "",
                    "expected": ""
                }
            ]
        },
    ]

    mode_files = []
    registry = {
        "equals": EqualsHandler,
    }

    for i, mode in enumerate(test_modes):
        file = tmp_path / f"mode_{i}.json"

        file.write_text(
            json.dumps(mode),
            encoding="utf-8"
        )

        mode_files.append(file)

    valid_modes, errors = prepare_modes(mode_files, registry)

    assert len(valid_modes) == 2
    assert len(errors) == 4
