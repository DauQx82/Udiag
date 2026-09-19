# Udiag 
> Working name. Planned name: **MyQDiag**
> An early Python prototype for discovering, validating, executing, and
> evaluating declarative JSON scenarios.

> **Status:** The current runtime validates JSON modes and executes their
> operations, but still presents raw command output. The handler pipeline
> described below is under development.
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
does not need to be changed before the first complete pipeline works.

## Target pipeline

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
The prototype can already discover handler files, load their modules dynamically,
locate concrete `BaseHandler` implementations, and build a handler registry.
Handler validation and runtime dispatch are not connected to scenarios yet.

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
- subprocess execution with captured stdout, stderr, and return code
- `OperationResult` and `HandlerResult` data models
- an abstract `BaseHandler` API and an `EqualsHandler` skeleton
- handler-file discovery and recoverable dynamic module loading
- concrete `BaseHandler` class discovery and handler registry construction
- collection of errors from invalid or incomplete handler modules
- the original diagnostic CLI and Ubuntu-oriented example modes
- pytest tests for validation, mode preparation, and CLI parsing

The current runtime still follows this shorter path:

```text
JSON mode → Udiag CLI → subprocess → selected program → raw output
```

The terminal currently displays stdout and the return code; captured stderr is
not presented.

The missing connection is:

```text
handler registry
    → use the selected handler during scenario validation
    → call handler.validate_config(...)
    → execute and create OperationResult
    → call handler.evaluate(...)
    → return HandlerResult
```

The first milestone is one complete end-to-end flow:

```text
one JSON scenario
    → one operation
    → dynamically discovered "equals" handler
    → handler-specific validation
    → execution
    → OperationResult
    → handler.evaluate(...)
    → HandlerResult
```

Additional handlers, interpreters, and larger architectural changes should come
after this flow works.

## Requirements

- Python 3.12 or newer
- `pytest` for running the test suite
- the programs referenced by an executed scenario

The runtime currently uses only the Python standard library.

## Project structure

- `udiag.py` — current diagnostic CLI and operation execution
- `mode_manager.py` — JSON mode discovery, loading, and structural validation
- `handler_manager.py` — handler discovery, dynamic loading, class validation, and registry construction
- `structure.py` — typed configuration structures and result models
- `terminal.py` — current terminal presentation
- `modes/` — Ubuntu-oriented JSON scenarios
- `handlers/` — `BaseHandler`, the `EqualsHandler` skeleton, and placeholders
- `tests/` — validation, mode-preparation, and CLI tests

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

# Show mode-configuration errors
python3 udiag.py --errors
```

`run` currently executes operations and displays raw results. Handler evaluation
is not connected to execution yet.

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
Handler-specific fields should be validated by the selected handler; in this
example, `expected` belongs to `equals`. The prototype still performs some of
this validation centrally while the handler pipeline is being connected.

Programs are started from an argument list with `shell=False`; scenarios do not
contain shell command strings.

## Tests

```bash
python3 -m pytest
```

The current tests cover mode and operation validation, preparation of valid
modes, and CLI parsing. Handler loading and the complete evaluation pipeline
need further coverage as they are connected.

## Security

Only run scenario files you trust. `shell=False` prevents shell parsing, but the
engine does not sandbox executables or restrict which programs and arguments a
scenario may request. Trust metadata and output sanitization are not implemented
yet.

## Next steps

1. connect the handler registry to scenario validation
2. delegate handler-specific configuration validation to the selected handler
3. complete `EqualsHandler.evaluate()`
4. connect `OperationResult` to handler evaluation and produce `HandlerResult`
5. test the first complete end-to-end pipeline
6. separate the neutral engine from Udiag diagnostics incrementally

## License

Copyright © 2026 DauQx82

This project is licensed under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`). See [LICENSE](LICENSE) for the full license text.
