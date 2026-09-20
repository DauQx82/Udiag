# Udiag

> Working name. Planned name: **MyQDiag**
>
> An early Python prototype for discovering, validating, executing, and
> evaluating declarative JSON scenarios.

> **Status:** The current runtime validates JSON modes, selects dynamically
> discovered handlers, executes operations, and evaluates their results through
> the handler pipeline. Terminal presentation is still minimal.
>
> Changes from each development session are published incrementally, so the
> repository may contain transitional code between milestones.

## Overview

Udiag began as a personal helper for repeatable GNU/Linux diagnostics, developed
primarily on Ubuntu. The project is now moving toward a clearer separation
between two layers:

1. **Scenario engine** — a small core for discovering JSON scenarios, validating
   them, executing operations, selecting handlers, and returning standardized
   results.
2. **Udiag diagnostics** — GNU/Linux scenarios, tool-specific interpreters, and
   diagnostic presentation built on top of that engine.

Scenario files define **what** should be executed. The engine is intended to
provide **how** scenarios are discovered, validated, executed, and evaluated.
It should not contain built-in knowledge of Ubuntu, `systemctl`, `journalctl`,
or `dpkg`.

The current code still calls scenarios *modes*. This transitional terminology
can remain until naming is addressed as a separate cleanup.

## Pipeline

```text
JSON scenario
    ↓
discovery and loading
    ↓
common structural validation
    ↓
handler lookup and dynamic loading
    ↓
handler.validate_config(...)
    ↓
operation execution
    ↓
OperationResult
    ↓
handler.evaluate(...)
    ↓
HandlerResult
```

### Target responsibilities

In the target design, the **engine** owns discovery, JSON loading, validation of
common operation fields, execution, raw result collection, handler dispatch,
and predictable handling of configuration or loading errors.

**Handlers** are reusable evaluation strategies such as `equals`, `contains`,
`empty`, and `information`. They are intended to implement the `BaseHandler`
API, validate their own configuration, evaluate an `OperationResult`, and
return a `HandlerResult`.

For example, the engine can require `title`, `program`, `args`, and `handler`,
while the `equals` handler should decide whether its `expected` field is valid.
The prototype discovers and loads Python modules from `handlers/`, locates
concrete `BaseHandler` implementations, and builds a handler registry. The
selected handler validates its operation configuration and evaluates the
result at runtime.

**Interpreters** are a later, optional layer for normalizing complex,
tool-specific output before a handler evaluates it. An interpreter understands
a data format; a handler evaluates the normalized result. Their API will be
designed only when a concrete use case requires it.

## Scope

The engine is intended to be generic only as far as real project needs require:

```text
scenario → operation → execution → optional interpretation → evaluation → result
```

It is not currently intended to become a universal workflow framework, a
continuous monitoring system, a configuration-management platform, or an
automated remediation system. New abstractions should follow working use cases
rather than anticipate every possible workflow.

## Current state

Implemented or started:

- JSON mode discovery, loading, and common structural validation
- handler-file discovery, recoverable dynamic module loading, and registry
  construction from concrete `BaseHandler` implementations
- registry-backed handler lookup during scenario validation
- handler-specific configuration validation delegated to the selected handler
- subprocess execution with captured stdout, stderr, return code, and a
  ten-second timeout
- separate `Operation`, `OperationResult`, and `HandlerResult` data models
- runtime dispatch of operation results to dynamically selected handlers
- a working `EqualsHandler` that evaluates stdout and returns `HandlerResult`
- basic terminal presentation of handler success or failure and actual output
- the original diagnostic CLI and Ubuntu-oriented example modes
- pytest tests for handler loading and registry construction, handler
  evaluation, mode preparation, and CLI parsing

The first end-to-end milestone is now working:

```text
JSON scenario
    → common structural validation
    → registry lookup and handler.validate_config(...)
    → operation execution
    → OperationResult
    → handler.evaluate(...)
    → HandlerResult
    → terminal presentation
```

The terminal currently shows an `OK` or `FAIL` result together with the actual
value produced by the handler. Captured stderr, the return code, and richer
diagnostic context are not presented yet. Additional handlers, interpreters,
and larger architectural changes should follow concrete MVP needs.

## Requirements

- Python 3.12 or newer
- `pytest` for running the test suite
- the programs referenced by an executed scenario

The runtime currently uses only the Python standard library.

## Project structure

- `udiag.py` — current diagnostic CLI and operation execution
- `mode_manager.py` — JSON mode discovery, loading, and structural validation
- `handler_manager.py` — handler discovery, dynamic module loading, class
  validation, and registry construction
- `structure.py` — typed configuration structures and result models
- `terminal.py` — current terminal presentation
- `modes/` — Ubuntu-oriented JSON scenarios
- `handlers/` — `BaseHandler`, the working `EqualsHandler`, and placeholders
- `tests/` — handler, validation, mode-preparation, and CLI tests

These names reflect the current prototype. Separating the engine from Udiag does
not require renaming every module in the same change.

## Current CLI

```bash
# General help
python3 udiag.py
python3 udiag.py --help

# Inspect a mode without executing it
python3 udiag.py show base
python3 udiag.py show system

# Run a mode
python3 udiag.py run base
python3 udiag.py run system

# Show collected configuration and handler errors
python3 udiag.py --errors
```

`run` validates each operation through its selected handler, executes the
program, evaluates the resulting `OperationResult`, and displays the resulting
`HandlerResult` as `OK` or `FAIL` with its actual value.

## JSON scenario format

A scenario is currently represented as a JSON mode containing metadata and an
ordered list of operations:

```json
{
  "name": "base",
  "description": "Basic system diagnostic",
  "operations": [
    {
      "title": "System state",
      "program": "systemctl",
      "args": ["is-system-running"],
      "handler": "equals",
      "expected": "running"
    }
  ]
}
```

Common operation fields are `title`, `program`, `args`, and `handler`.
Common fields are validated by the mode manager, while handler-specific fields
are validated by the selected handler. In this example, `expected` belongs to
`equals`. An operation is accepted only when its common structure is valid, its
handler exists in the registry, and the handler accepts its configuration.

Programs are started from an argument list with `shell=False`; scenarios do not
contain shell command strings.

## Tests

```bash
python3 -m pytest
```

The current tests cover handler discovery, dynamic loading and registry
construction, `EqualsHandler` evaluation, mode and operation validation,
registry-backed handler configuration checks, preparation of valid modes, and
CLI parsing. A full subprocess-to-terminal integration test is still to be
added.

## Security

Only run scenario files you trust. `shell=False` prevents shell parsing, but the
engine does not sandbox executables or restrict which programs and arguments a
scenario may request. Trust metadata and output sanitization are not implemented
yet.

## Next steps

1. improve the `base` scenario into a useful MVP diagnostic
2. improve presentation of `HandlerResult` and relevant execution details
3. separate handler-loading, scenario-validation, and runtime errors clearly
4. turn subprocess timeouts and execution failures into normal operation results
5. add final end-to-end coverage for execution and terminal presentation
6. separate the neutral engine from Udiag diagnostics incrementally

## License

Copyright © 2026 DauQx82

This project is licensed under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`). See [LICENSE](LICENSE) for the full license text.
