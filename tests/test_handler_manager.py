# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from types import ModuleType

from handler_manager import find_handlers, build_handler_map, load_handler

def test_handler_manager_loads_equals():

    handlers = find_handlers()

    assert handlers[0] is True

    handler_map_result = build_handler_map(handlers)

    assert handler_map_result[0] is True

    handler_map = handler_map_result[1]

    assert "equals" in handler_map

    equals_file = handler_map["equals"]

    success, result = load_handler(equals_file)

    assert handlers is not None
    assert isinstance(handlers, tuple)

    assert len(handler_map_result[1]) == 4

    assert success is True
    assert isinstance(result, ModuleType)
    assert result.__name__ == "handlers.equals"