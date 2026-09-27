# Udiag

> **Udiag** is the current working name; **MyQDiag** is the planned name.

Udiag is a small Python application for running repeatable GNU/Linux diagnostic
scenarios described in JSON. It discovers and validates scenarios, executes
their operations, evaluates selected process-result values with reusable
handlers, and presents a compact terminal report.

The project is an educational, hobbyist open-source project and a practical
personal diagnostic tool. It is currently at the working MVP stage: the complete
path from JSON discovery to terminal presentation is implemented, while the
scenario library and higher-level interpretation remain intentionally small.

## How it works

```text
JSON mode
    -> discovery and loading
    -> structural validation
    -> checks normalized as source + handler + config
    -> handler registry and configuration validation
    -> Operation
    -> subprocess execution
    -> OperationResult(stdout, stderr, returncode)
    -> source selection
    -> BaseHandler(actual, config)
    -> HandlerResult for every check
    -> operation-wide AND aggregation
    -> terminal presentation
```

A completed process always produces three independent data sources:

- `stdout` as a string;
- `stderr` as a string;
- `returncode` as an integer.

Each scenario decides which sources matter and how to evaluate them. A non-zero
return code is data, not an execution error by itself.

For example:

```json
"checks": {
    "stdout": {
        "equals": "running"
    },
    "stderr": {
        "empty": true
    },
    "returncode": {
        "equals": 0
    }
}
```

The engine selects a source. A handler evaluates only the resulting `actual`
value against its own `config`. All declared checks are evaluated, and the
operation succeeds only when all of them succeed.

## Result semantics

Udiag distinguishes three runtime outcomes:

- **SUCCESS** — the process completed and every declared check succeeded;
- **FAILURE** — the process completed normally, but at least one check failed;
- **ERROR** — no normal `OperationResult` was obtained because the executable
  was missing, permission was denied, or the ten-second timeout expired.

A runtime error in one operation does not prevent later operations from running.
Unexpected programming exceptions are not silently converted into diagnostic
errors.

## Included modes

The repository includes three initial GNU/Linux diagnostic modes containing 18
operations in total:

### `base`

Core operating-system checks:

- overall systemd state;
- failed systemd units;
- `systemd-journald` service state;
- Debian package database audit;
- package dependency consistency;
- system clock synchronization;
- root filesystem read-write state;
- kernel and system information.

### `storage`

Filesystem and block-device checks:

- root mount availability;
- `/etc/fstab` verification;
- filesystem space usage;
- inode usage;
- block-device overview.

### `network`

Local network and DNS checks:

- configured network addresses;
- default route availability;
- route lookup toward an external address;
- public DNS resolution;
- listening TCP sockets.

The included scenarios target a systemd-based Ubuntu or Debian installation and
use common system utilities without `sudo`. Informational operations use the
`pass` handler: run a mode with `--details` to display their collected output.

## Built-in handlers

Handlers implement generic conditions. They do not contain knowledge about
particular programs.

| Handler | Accepted config | Condition |
| --- | --- | --- |
| `equals` | string or integer | `actual` equals the configured value. |
| `contains` | string | Textual `actual` contains the configured substring. |
| `empty` | `true` | Textual `actual` is empty after removing trailing line endings. |
| `pass` | `true` | Always succeeds and preserves `actual` for presentation. |

Handler modules are discovered dynamically from `handlers/*.py`. Their filename
stem is the name used in JSON, so adding a valid handler does not require editing
a central registry list.

## Usage

Requirements:

- Python 3.12 or newer;
- the external programs referenced by the selected mode.

The Udiag runtime itself uses only the Python standard library.

Run commands from the repository root:

```bash
# General help
python3 udiag.py
python3 udiag.py --help

# List valid modes
python3 udiag.py list

# Show mode metadata and operations without executing them
python3 udiag.py show base

# Run a mode
python3 udiag.py run base
python3 udiag.py run storage
python3 udiag.py run network

# Show every successful check and informational value
python3 udiag.py run base --details

# Show scenario and handler configuration problems
python3 udiag.py --errors

# Display application information
python3 udiag.py about
```

Modes are discovered and validated before the CLI parser is built. Invalid
operation objects are reported and skipped while valid sibling operations are
kept. A mode with no valid operations is not exposed as a `run` or `show`
choice.

## Scenario format

A mode is a JSON object containing:

- `name`;
- `description`;
- a non-empty `operations` array.

Every operation defines `title`, `program`, `args`, and a non-empty `checks`
object. Programs are executed from an argument list with no shell parsing.

See [modes/README.md](modes/README.md) for:

- the complete JSON contract;
- the `source -> handler -> config` model;
- validation rules and common errors;
- verified example scenarios;
- instructions for adding a new mode.

## Handler development

The core handler contract is:

```text
actual + config -> HandlerResult
```

The engine selects the process-result source. A handler understands a condition,
not the program that produced the value.

See [handlers/README.md](handlers/README.md) for:

- the `BaseHandler` API;
- exact built-in-handler behavior;
- dynamic discovery requirements;
- a complete example custom handler.

## Project structure

- `udiag.py` — CLI, subprocess execution, source selection, and check dispatch;
- `mode_manager.py` — mode discovery, JSON loading, validation, and
  normalization;
- `handler_manager.py` — dynamic handler discovery, loading, class validation,
  and registry construction;
- `structure.py` — operation, check, result, and outcome models;
- `terminal.py` — terminal status and details presentation;
- `state.py` — collected mode and handler configuration errors;
- `modes/` — JSON scenarios and scenario-authoring documentation;
- `handlers/` — generic condition handlers and handler-authoring documentation;
- `tests/` — automated tests when included in the development checkout.

## Development checks

When the test suite and `pytest` development dependency are available:

```bash
python3 -m pytest
```

The source can also be checked for syntax errors without third-party packages:

```bash
python3 -m compileall .
```

## Current limitations

- The scenario format supports implicit AND aggregation only; there is no
  `OR`/`NOT` expression language.
- The same handler name cannot be repeated under one source because handlers
  are JSON object keys.
- The execution timeout is fixed at ten seconds.
- Program-specific interpreters are not implemented yet.
- The `SKIP` outcome exists in the data and presentation model, but the current
  runner does not emit it.
- `udiag run` does not yet encode FAILURE or ERROR in its own process exit code.
- Udiag executes one mode locally and does not provide scheduling, continuous
  monitoring, remote execution, or automatic remediation.

## Security

Only run scenario files you trust. `shell=False` prevents shell parsing, but
Udiag does not sandbox executables or restrict which programs and arguments a
scenario may request. It also does not sanitize command output before terminal
presentation.

## Scope and direction

Udiag is not intended to become a universal workflow framework or configuration
management system. The neutral scenario engine should remain small. Future
program-specific interpreters may normalize complex diagnostic output, but they
should not replace generic handlers or move program knowledge into the engine.

## License

Copyright © 2026 DauQx82

This project is licensed under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`). See [LICENSE](LICENSE) for the full license text.
