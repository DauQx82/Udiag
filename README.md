# Udiag

A personal, scenario-driven helper for repeatable GNU/Linux diagnostics.

> **Project status:** Early prototype.
>
> Currently implemented:
> - discovery of JSON diagnostic modes
> - loading and structural validation of modes and operations
> - execution of configured programs through `subprocess`
> - capturing standard output, standard error, and return codes
>
> Current execution flow:
>
> `JSON mode → Udiag → subprocess → selected program → raw output`
>
> Automated tests currently cover mode and operation validation, mode
> preparation, and command-line argument parsing.
>
> Result handlers are currently under development.

## What is Udiag?

Udiag is a small personal tool for simple, repeatable and predictable tasks,
such as targeted system diagnostics and routine checks.

It started as a way to avoid manually repeating the same diagnostic commands
on known machines. Diagnostic procedures are described as JSON modes, while
Udiag handles their validation and execution.

The longer-term goal is to reduce raw command output into useful diagnostic
results while still keeping the original details available when needed.

## What Udiag is not

Udiag is not intended to be:

- a continuous monitoring system
- a configuration management or orchestration tool
- an automated remediation system
- a replacement for existing GNU/Linux diagnostic tools

Udiag is intended to use existing tools and make small, repeatable diagnostic
tasks easier to run and review.

## Platform scope

Udiag is currently developed and tested primarily on Ubuntu.

The bundled diagnostic modes use tools commonly available in Ubuntu/Debian
environments, such as `systemctl`, `hostnamectl`, `uname`, and `dpkg`.

The core is not intended to depend on those specific tools. Modes describe
which programs should be executed, so support for other environments can be
added through different modes and, later, tool-specific interpreters.

Ubuntu is the development/reference platform; the architecture is
intended to keep distribution-specific knowledge outside the core.

Cross-distribution compatibility is not currently tested or guaranteed.

## Intended design

A diagnostic scenario defines what should be checked. A mode is the current
JSON representation of such a scenario.

A scenario defines what should be checked. Udiag executes each operation and
captures its standard output, standard error, and return code.

Simple, reusable handlers are intended to evaluate generic conditions such as
equality, containment, or empty output. Tool-specific interpreters are intended
to understand more complex output formats.

Their results will be passed to presenters that produce concise,
human-readable reports while preserving raw details.

These components are part of the planned architecture and are not fully
implemented yet.

## Requirements

- Python 3.12 or newer
- Ubuntu or another system that provides the commands used by the selected mode

The runtime code currently uses only the Python standard library.
Running the test suite requires `pytest`.

## Project structure

- `udiag.py` — command-line interface and operation execution
- `mode_manager.py` — mode discovery, JSON loading, and structural validation
- `handler_manager.py` — handler discovery
- `structure.py` — typed mode/operation structures and the runtime `Operation` model
- `terminal.py` — terminal report output presentation
- `modes/base.json` — basic system-state diagnostic
- `modes/system.json` — extended system and package diagnostic
- `handlers/` — base handler API and placeholders for planned handler implementations

The `modes/` directory must be next to `mode_manager.py`.
The `handlers/` directory must be next to `handler_manager.py`.

## Usage

Run these commands from the project directory:

```bash
python3 udiag.py
python3 udiag.py --help
```

Running the program without a command displays the available commands. To see
the modes accepted by a command, open its help:

```bash
python3 udiag.py run --help
python3 udiag.py show --help
```

### Inspect a mode

`show` prints a mode description and its operations without executing them:

```bash
python3 udiag.py show base
python3 udiag.py show system
```

### Run a mode

`run` executes every operation in the selected mode in order:

```bash
python3 udiag.py run base
python3 udiag.py run system
```

### Show configuration errors

Invalid modes are excluded from the available CLI choices. Their validation
errors can be displayed with:

```bash
python3 udiag.py --errors
```

If some modes are invalid, a short warning is also printed before a valid mode
is shown or run.

## Bundled modes

- `base` — checks the overall system state with `systemctl`
- `system` — displays system and kernel information, checks system state and
  failed services, and runs a package audit

## Tests

Run all tests with:

```bash
python3 -m pytest
```

## JSON mode format

A mode contains its metadata and an ordered list of operations:

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

Current operation fields:

- `title` — human-readable operation name
- `program` — executable to start
- `args` — list of arguments passed to the executable
- `handler` — intended result evaluation strategy;
currently validated as metadata but not executed
- `expected` — `expected` — expected value; currently required by validation for the
  `equals` and `contains` handlers

Commands are started as an argument list with `shell=False`; the JSON does not
contain a shell command string.

## Current behavior and limitations

The current version:

- discovers `*.json` files in `modes/`
- validates JSON syntax and the presence/types of required top-level fields
- validates the basic structure of every operation
- excludes invalid modes and reports their errors
- provides `run`, `show`, and `--errors`
- captures standard output, standard error, and the process return code

This is still an early prototype. In particular:

- `handler` and `expected` are validated as metadata but are
  not yet used to interpret operation results
- terminal output is raw; there is no success/warning/failure interpretation
- standard error is captured but is not currently printed
- subprocess startup errors are not handled and operations have no timeout
- semantic validation is still limited and does not yet restrict handler
  names to the supported set
- reports are not sanitized and may include the local username, device
  hostname, or other environment-specific information

## Security

Only run mode files you trust. Using `shell=False` prevents shell parsing, but
Udiag does not sandbox executables or restrict what a mode can run. Review every
mode before executing it.

Trust metadata and output sanitization are not implemented yet.

## Planned work

- connect handlers and expected values to result interpretation
- show clear operation statuses
- validate handler names against the supported set
- handle missing executables, timeouts, and standard error cleanly
- sanitize reports before they are shared
- support optional aliases configured by the user

## License

Copyright © 2026 DauQx82

Udiag is licensed under the GNU General Public License
version 3 or later (`GPL-3.0-or-later`).

See [LICENSE](LICENSE) for the full license text.