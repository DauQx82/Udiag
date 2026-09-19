# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from handlers.equals import EqualsHandler

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
    assert {"expected": 42} not in result_list
    assert {"expected": None} not in result_list
    assert {"expected": {}} not in result_list
    assert {"expected": []} not in result_list
