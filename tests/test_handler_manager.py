# Copyright (C) 2026 DauQx82
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from types import ModuleType

import pytest

import handler_manager
from handlers.handler import BaseHandler


def test_find_handlers_discovers_only_handler_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_file = tmp_path / "__init__.py"
    handler_file = tmp_path / "handler.py"

    init_file.touch()
    handler_file.touch()

    equals_file = tmp_path / "equals.py"
    contains_file = tmp_path / "contains.py"
    ignored_file = tmp_path / "README.md"

    equals_file.touch()
    contains_file.touch()
    ignored_file.touch()

    monkeypatch.setattr(handler_manager, "HANDLERS_DIR", tmp_path)
    monkeypatch.setattr(handler_manager, "INIT_FILE", init_file)
    monkeypatch.setattr(handler_manager, "HANDLER_FILE", handler_file)

    result = handler_manager.find_handlers()

    assert result[0] is True

    discovered_names = {path.name for path in result[1]}

    assert discovered_names == {"equals.py", "contains.py"}


def test_find_handlers_fails_without_init_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_file = tmp_path / "__init__.py"
    handler_file = tmp_path / "handler.py"

    handler_file.touch()

    monkeypatch.setattr(handler_manager, "HANDLERS_DIR", tmp_path)
    monkeypatch.setattr(handler_manager, "INIT_FILE", init_file)
    monkeypatch.setattr(handler_manager, "HANDLER_FILE", handler_file)

    result = handler_manager.find_handlers()

    assert result[0] is False
    assert "__init__.py" in result[1]


def test_find_handlers_fails_without_handler_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_file = tmp_path / "__init__.py"
    handler_file = tmp_path / "handler.py"

    init_file.touch()

    monkeypatch.setattr(handler_manager, "HANDLERS_DIR", tmp_path)
    monkeypatch.setattr(handler_manager, "INIT_FILE", init_file)
    monkeypatch.setattr(handler_manager, "HANDLER_FILE", handler_file)

    result = handler_manager.find_handlers()

    assert result[0] is False
    assert "handler.py" in result[1]


def test_build_handler_map_uses_file_stems_as_names() -> None:
    handler_files = [
        Path("/tmp/equals.py"),
        Path("/tmp/contains.py"),
    ]

    discovery_result: handler_manager.FindHandlersSuccess = (
        True,
        handler_files,
    )

    result = handler_manager.build_handler_map(discovery_result)

    assert result == {
        "equals": Path("/tmp/equals.py"),
        "contains": Path("/tmp/contains.py"),
    }


def test_load_handler_loads_valid_module(tmp_path: Path) -> None:
    handler_file = tmp_path / "test_valid_module.py"
    handler_file.write_text(
        "VALUE = 42\n",
        encoding="utf-8",
    )

    result = handler_manager.load_handler(handler_file)

    assert result[0] is True
    assert getattr(result[1], "VALUE") == 42


def test_load_handler_reports_module_execution_error(tmp_path: Path) -> None:
    handler_file = tmp_path / "test_broken_module.py"
    handler_file.write_text(
        "raise RuntimeError('boom')\n",
        encoding="utf-8",
    )

    result = handler_manager.load_handler(handler_file)

    assert result[0] is False
    assert "Failed to load handler" in result[1]
    assert "boom" in result[1]


def test_find_handler_class_finds_single_local_handler() -> None:
    module = ModuleType("handlers.test_valid")

    class ValidHandler(BaseHandler):
        @classmethod
        def validate_config(cls, operation: object) -> bool:
            return True

        def evaluate(self):
            raise NotImplementedError

    ValidHandler.__module__ = module.__name__
    setattr(module, "ValidHandler", ValidHandler)

    result = handler_manager.find_handler_class(module)

    assert result[0] is True
    assert result[1] is ValidHandler


def test_find_handler_class_ignores_imported_handler() -> None:
    module = ModuleType("handlers.test_imported")

    class ExternalHandler(BaseHandler):
        @classmethod
        def validate_config(cls, operation: object) -> bool:
            return True

        def evaluate(self):
            raise NotImplementedError

    ExternalHandler.__module__ = "handlers.some_other_module"
    setattr(module, "ExternalHandler", ExternalHandler)

    result = handler_manager.find_handler_class(module)

    assert result[0] is False
    assert "No BaseHandler subclass" in result[1]


def test_find_handler_class_fails_when_no_classes_exist() -> None:
    module = ModuleType("handlers.test_empty")

    result = handler_manager.find_handler_class(module)

    assert result[0] is False
    assert "No classes found" in result[1]


def test_find_handler_class_rejects_multiple_handlers() -> None:
    module = ModuleType("handlers.test_multiple")

    class FirstHandler(BaseHandler):
        @classmethod
        def validate_config(cls, operation: object) -> bool:
            return True

        def evaluate(self):
            raise NotImplementedError

    class SecondHandler(BaseHandler):
        @classmethod
        def validate_config(cls, operation: object) -> bool:
            return True

        def evaluate(self):
            raise NotImplementedError

    FirstHandler.__module__ = module.__name__
    SecondHandler.__module__ = module.__name__
    
    setattr(module, "FirstHandler", FirstHandler)
    setattr(module, "SecondHandler", SecondHandler)

    result = handler_manager.find_handler_class(module)

    assert result[0] is False
    assert "Found 2 BaseHandler subclasses" in result[1]


def test_find_handler_class_rejects_abstract_handler() -> None:
    module = ModuleType("handlers.test_abstract")

    class AbstractHandler(BaseHandler):
        @classmethod
        def validate_config(cls, operation: object) -> bool:
            return True

    AbstractHandler.__module__ = module.__name__
    setattr(module, "AbstractHandler", AbstractHandler)

    result = handler_manager.find_handler_class(module)

    assert result[0] is False
    assert "is abstract" in result[1]
    assert "evaluate" in result[1]


def test_build_handler_registry_keeps_valid_handlers_and_collects_errors(
    tmp_path: Path,
) -> None:
    valid_file = tmp_path / "test_registry_valid.py"
    invalid_file = tmp_path / "test_registry_invalid.py"

    valid_file.write_text(
        """
from handlers.handler import BaseHandler


class ValidHandler(BaseHandler):
    @classmethod
    def validate_config(cls, operation):
        return True

    def evaluate(self):
        raise NotImplementedError
""",
        encoding="utf-8",
    )

    invalid_file.write_text(
        """
VALUE = 42
""",
        encoding="utf-8",
    )

    handlers_map = {
        "valid": valid_file,
        "invalid": invalid_file,
    }

    registry, errors = handler_manager.build_handler_registry(handlers_map)

    assert "valid" in registry
    assert registry["valid"].__name__ == "ValidHandler"

    assert "invalid" not in registry

    assert len(errors) == 1
    assert "No classes found" in errors[0]


def test_build_handler_registry_collects_import_errors(
    tmp_path: Path,
) -> None:
    broken_file = tmp_path / "test_registry_broken.py"
    broken_file.write_text(
        "raise RuntimeError('registry boom')\n",
        encoding="utf-8",
    )

    registry, errors = handler_manager.build_handler_registry(
        {"broken": broken_file}
    )

    assert registry == {}
    assert len(errors) == 1
    assert "registry boom" in errors[0]


def test_build_handler_registry_accepts_empty_map() -> None:
    registry, errors = handler_manager.build_handler_registry({})

    assert registry == {}
    assert errors == []