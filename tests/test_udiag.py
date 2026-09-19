# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from udiag import get_mode_names, build_parser

# README!
# type: ignore[arg-type] ← I use this construct so that Pylance doesn't report a type error.
# This helps with further work because I can immediately see actual errors.

def test_get_mode_names_empty():
    assert get_mode_names([]) == []

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

    result = get_mode_names(modes) #type: ignore[arg-type]

    assert result == ["base", "system"]

def test_parser_run():
    modes = [
        {
            "name": "base",
            "description": "Base diagnostic",
            "operations": []
        }
    ]

    parser = build_parser(modes) #type: ignore[arg-type]
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

    parser = build_parser(modes) #type: ignore[arg-type]
    args = parser.parse_args(["show", "base"])

    assert args.command == "show"
    assert args.mode == "base"

def test_parser_errors():
    parser = build_parser([])

    args = parser.parse_args(["--errors"])

    assert args.mode_errors is True
