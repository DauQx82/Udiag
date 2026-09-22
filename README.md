# Udiag

> **Udiag** is the current working name; **MyQDiag** is the planned name.
>
> This is an early-stage Python prototype for discovering, validating,
> executing, and evaluating declarative JSON scenarios.
>
> **Status:** The first end-to-end path works for modes backed by a valid
> handler. The runtime validates JSON modes, selects handlers from a dynamically
> built registry, executes operations, and evaluates their results. Terminal
> output remains minimal.
>
> Changes are published after each development session, so the repository may
> temporarily contain transitional code between milestones.

## Overview

Udiag started as a personal helper for repeatable GNU/Linux diagnostics,
developed primarily on Ubuntu. It is now evolving into two clearly separated
layers:

1. **Scenario engine** — a small core for discovering and validating JSON
   scenarios, executing their operations, selecting handlers, and returning
   standardized results.
2. **Udiag diagnostic layer** — GNU/Linux scenarios, tool-specific interpreters,
   and diagnostic presentation built on top of the engine.

Scenario files define **what** to execute; the engine defines **how** they are
discovered, validated, executed, and evaluated. The engine should not contain
built-in knowledge of Ubuntu, `systemctl`, `journalctl`, or `dpkg`.

The code still uses the term *mode* for scenarios. This terminology will be
cleaned up separately.

## Architecture

```text
JSON scenario
    ↓
discovery and loading
    ↓
common structural validation
    ├── invalid → scenario error
    ↓
handler registry lookup
    ├── handler unavailable → scenario error
    ↓
handler.validate_config(...)
    ├── invalid configuration → scenario error
    ↓
Operation
    ↓
operation execution
    │
    ├── execution failure
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutExpired
    │           ↓
    │   OperationFailure
    │   (False, Exception)
    │           ↓
    │   OperationOutcome
    │           ↓
    │   terminal presentation → ERROR
    │
    └── completed execution
            ↓
        OperationResult
            ↓
        handler.evaluate(...)
            ↓
        HandlerResult
            ↓
        OperationSuccess
        (True, HandlerResult)
            ↓
        OperationOutcome
            ↓
        terminal presentation
            ├── success = True  → OK
            └── success = False → FAIL
```

### Target responsibilities

In the intended design, the **engine** handles scenario discovery, JSON loading,
validation of shared operation fields, execution, raw result collection,
handler dispatch, and predictable configuration and loading errors.

**Handlers** are reusable evaluation strategies such as `equals`, `contains`,
`empty`, and `information`. They are intended to implement the `BaseHandler`
API, validate their own configuration, evaluate an `OperationResult`, and
return a `HandlerResult`.

The engine validates shared fields such as `title`, `program`, `args`, and
`handler`, while each handler validates fields specific to its strategy. For
example, `expected` belongs to the `equals` handler. The engine discovers
concrete `BaseHandler` implementations in `handlers/`, loads them, and builds
the registry used during validation and execution.

**Interpreters** are a later, optional layer for normalizing complex,
tool-specific output before a handler evaluates it. An interpreter understands
a data format; a handler evaluates the normalized result. Their API will be
designed only when a concrete use case requires it.

## Scope

The engine is generalized only in response to concrete project needs.

It is not intended to become a universal workflow framework, continuous
monitoring system, configuration-management platform, or automated remediation
system. New abstractions will be introduced only for demonstrated use cases.

## Current state

Currently implemented:

- JSON mode discovery, loading, and common structural validation
- handler module discovery, recoverable dynamic loading, concrete class
  validation, and registry construction
- registry-backed handler lookup and handler-specific configuration validation
- subprocess execution with captured stdout, stderr, and return codes, plus a
  ten-second timeout
- controlled handling of missing executables, permission errors, and timeouts
  without terminating the remaining scenario
- runtime dispatch to dynamically selected handlers and a working
  `EqualsHandler`
- separate `Operation`, `OperationResult`, and `HandlerResult` data models, with
  type aliases describing evaluated results and execution errors
- basic terminal presentation of `OK`, `FAIL`, and `ERROR`, including the actual
  value for evaluated results
- the original diagnostic CLI and Ubuntu-oriented example modes

The first complete path currently runs the `base` mode through `EqualsHandler`.
The `contains`, `empty`, and `information` modules are still placeholders, so
`system.json` is rejected during validation and is not exposed as a CLI choice.
Interpreters are not implemented yet.

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
- `state.py` — collected handler and mode errors used by `--errors`
- `terminal.py` — current terminal presentation
- `modes/` — Ubuntu-oriented JSON scenarios
- `handlers/` — `BaseHandler`, the working `EqualsHandler`, and placeholder
  modules
- `tests/` — handler, validation, mode-preparation, and CLI tests

These names reflect the current prototype. Separating the engine from Udiag does
not require renaming every module in the same change.

## Usage

```bash
# General help
python3 udiag.py
python3 udiag.py --help

# Inspect the currently valid mode without executing it
python3 udiag.py show base

# Run the currently valid mode
python3 udiag.py run base

# Run the currently valid mode with details
python3 udiag.py run base --details

# Show collected configuration and handler errors
python3 udiag.py --errors
```

Modes are loaded and validated before the CLI parser is built. `run` executes an
accepted mode, passes each successful `OperationResult` to the selected handler,
and displays its `HandlerResult` as `OK` or `FAIL`. Execution failures are shown
separately as `ERROR`.

The work-in-progress `system` mode is not currently available through `run` or
`show`; `--errors` explains which placeholder handlers prevent it from loading.

## JSON scenario format

Scenarios are currently stored as JSON mode files. Each file contains metadata
and an ordered list of operations:

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

The mode manager validates the shared fields: `title`, `program`, `args`, and
`handler`. Handler-specific fields are validated by the selected handler. In
this example, `expected` belongs to `equals`. An operation is accepted only if
its shared structure is valid, its handler exists in the registry, and that
handler accepts its configuration.

Programs are started from an argument list with `shell=False`; scenarios do not
contain shell command strings.

## Tests

```bash
python3 -m pytest
```

The test suite covers handler discovery, dynamic loading and registry
construction, `EqualsHandler` evaluation, mode and operation validation,
handler-specific configuration checks, preparation of valid modes, CLI parsing,
expected execution failures, and dispatch of successful results to handlers.
End-to-end coverage from a real subprocess through terminal presentation is
still pending.

## Security

Only run scenario files you trust. `shell=False` prevents shell parsing, but the
engine does not sandbox executables or restrict which programs and arguments a
scenario may request. Trust metadata and output sanitization are not implemented
yet.

## Next steps

1. Improve the `base` scenario into a useful MVP diagnostic
2. Improve presentation of `HandlerResult` and relevant execution details
3. Clarify handler-loading, scenario-validation, and runtime-error reporting
4. Add end-to-end coverage for execution and terminal presentation
5. Continue separating the neutral engine from Udiag diagnostics

## License

Copyright © 2026 DauQx82

This project is licensed under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`). See [LICENSE](LICENSE) for the full license text.
