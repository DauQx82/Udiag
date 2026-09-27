# Handlers

Handlers evaluate individual conditions against values produced by a completed
process.

> **A handler understands a condition, not a program.**

A handler does not know whether Udiag executed `systemctl`, `journalctl`,
`uname`, or another command. It also does not select `stdout`, `stderr`, or
`returncode`. The engine selects one source from `OperationResult` and passes
only its value to the handler.

The runtime flow is:

```text
OperationResult
-> source selection
-> BaseHandler(actual, config)
-> evaluate()
-> HandlerResult
```

## `BaseHandler` contract

`handlers/handler.py` defines the abstract base class used by every discovered
handler. Its input value type is currently:

```python
type CheckValue = str | int
```

`stdout` and `stderr` provide strings. `returncode` provides an integer.

The base constructor stores two values:

```python
BaseHandler(actual, config)
```

- `actual` is the selected runtime value;
- `config` is the JSON value declared under the handler's name.

Every concrete handler must implement two methods.

### `validate_config()`

```python
@classmethod
def validate_config(cls, config: object) -> bool:
    ...
```

This method is called while mode files are prepared, before their operations
are executed. It validates only the handler's configuration. Returning `False`
makes the containing operation invalid.

The method must not depend on process output because `actual` does not exist at
configuration time. A handler may accept a simple scalar, such as a string or
integer, or validate its own more complex JSON structure.

### `evaluate()`

```python
def evaluate(self) -> HandlerResult:
    ...
```

This method evaluates `self.actual` against `self.config` and returns a
`HandlerResult`:

| Field | Type | Meaning |
| --- | --- | --- |
| `success` | boolean | Whether the condition was satisfied. |
| `actual` | string or integer | Actual value reported to the presenter, optionally normalized by the handler. |
| `expected` | string, integer, or `None` | Expected value reported to the presenter. |

A normal condition mismatch should return `HandlerResult(success=False, ...)`.
The current evaluation loop does not convert unexpected handler exceptions into
operation errors, so handlers should not raise exceptions for ordinary
mismatches.

## Built-in handlers

The current source tree contains four concrete handlers.

### `equals`

File: `equals.py`  
Class: `EqualsHandler`

- Config: a JSON string or integer. Booleans and other JSON types are rejected.
- Condition: `actual == config`.
- If `actual` is a string, trailing `\r` and `\n` characters are removed before
  comparison. Other whitespace is preserved.
- Works with text sources and integer `returncode` values when the config has
  the corresponding type.

```json
"stdout": {
    "equals": "running"
}
```

```json
"returncode": {
    "equals": 0
}
```

### `contains`

File: `contains.py`  
Class: `ContainsHandler`

- Config: a JSON string.
- Condition: the configured string occurs inside `actual`.
- Matching is case-sensitive.
- `actual` must be a string; an integer actual value produces a failed result.
- No newline or whitespace normalization is performed.

```json
"stdout": {
    "contains": "active"
}
```

### `empty`

File: `empty.py`  
Class: `EmptyHandler`

- Config: exactly the JSON boolean `true`.
- `actual` must be a string.
- Trailing `\r` and `\n` characters are removed, then the result is compared
  with an empty string.
- Spaces, tabs, and other characters still make the value non-empty.
- An integer actual value produces a failed result.

```json
"stderr": {
    "empty": true
}
```

### `pass`

File: `pass.py`  
Class: `PassHandler`

- Config: exactly the JSON boolean `true`.
- Always returns a successful result.
- Preserves `actual` and reports `expected=None`.
- Can be used with any current source when a value should be collected and
  displayed without imposing a condition on it.

```json
"stdout": {
    "pass": true
}
```

## Adding a handler

1. Create a Python file directly inside `handlers/`. The filename stem becomes
   the handler name used in mode JSON. For example, `starts_with.py` is used as
   `"starts_with"`.
2. Define exactly one concrete class in that module that inherits
   `BaseHandler`.
3. Implement `validate_config()` as a class method.
4. Implement `evaluate()` and return a `HandlerResult` for both matching and
   non-matching values.
5. Keep the handler independent of program names and source selection.
6. Restart Udiag and run `python3 udiag.py --errors` to check discovery and mode
   configuration.
7. Reference the new handler by its filename stem in a mode.

Use a normal Python module name, preferably lowercase with underscores.

## Example custom handler

Create `handlers/starts_with.py`:

```python
from typing import cast

from .handler import BaseHandler
from structure import HandlerResult


class StartsWithHandler(BaseHandler):
    @classmethod
    def validate_config(cls, config: object) -> bool:
        return isinstance(config, str)

    def evaluate(self) -> HandlerResult:
        expected = cast(str, self.config)
        actual = self.actual

        success = (
            isinstance(actual, str)
            and actual.startswith(expected)
        )

        return HandlerResult(
            success=success,
            actual=actual,
            expected=expected,
        )
```

Use it in a mode as follows:

```json
"stdout": {
    "starts_with": "Linux"
}
```

The handler validates only its string configuration. During evaluation it also
checks the runtime type of `actual`, because source selection is outside the
handler and the base API allows both strings and integers.

## Dynamic discovery and registry requirements

No central handler list needs to be edited. At startup, Udiag:

1. checks that `handlers/__init__.py` and `handlers/handler.py` exist;
2. scans `handlers/*.py` directly inside the directory;
3. excludes `__init__.py` and `handler.py`;
4. loads every remaining file as `handlers.<filename-stem>`;
5. looks for concrete `BaseHandler` subclasses defined by that module;
6. registers the single valid class under the filename stem.

A handler module is rejected and reported when:

- it cannot be imported;
- it defines no `BaseHandler` subclass;
- it defines more than one `BaseHandler` subclass;
- its only handler class is still abstract.

Imported classes are not counted as handlers defined by the module. Handler
files in nested directories are not discovered. If a handler is rejected, it
is omitted from the registry, and mode operations referring to its name fail
configuration validation.
