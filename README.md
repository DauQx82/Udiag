# udiag

`udiag` is an early Python prototype for running repeatable Ubuntu diagnostic
procedures defined in JSON files.

The project separates the description of a diagnostic procedure from the code
that loads, validates, executes, and presents it. Future versions are intended
to interpret command results and sanitize reports, instead of leaving that work
to the user.

## Requirements

- Ubuntu or another system that provides the commands used by a selected mode
- Python 3.12 or newer

The Python code currently uses only the standard library. The bundled modes use
`systemctl`, `hostnamectl`, `uname`, and `dpkg`.

## Project structure

- `udiag.py` — command-line interface and operation execution
- `mode_manager.py` — mode discovery, JSON loading, and structural validation
- `structure.py` — typed mode/operation structures and the runtime `Operation`
  model
- `terminal.py` — terminal report output presentation
- `modes/base.json` — basic system-state diagnostic
- `modes/system.json` — extended system and package diagnostic

The `modes/` directory must be next to `mode_manager.py`.

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
- `handler` — intended result interpreter
- `expected` — required for the `equals` and `contains` handlers

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
  not yet used to interpret 
- terminal output is raw; there is no success/warning/failure interpretation
- standard error is captured but is not currently printed
- subprocess startup errors are not handled and operations have no timeout
- semantic validation is still limited and does not yet restrict handler
- reports are not sanitized and include the local username and device hostname

## Security

Only run mode files you trust. Using `shell=False` prevents shell parsing, but a
mode can still request any installed executable with arbitrary arguments. Risk
classification, confirmation for system-changing operations, trust metadata,
and output sanitization are planned but are not implemented yet.

## Planned work

- connect handlers and expected values to result interpretation
- show clear operation statuses
- validate supported handler
- handle missing executables, timeouts, and standard error cleanly
- add risk levels and confirmation for system-changing operations
- sanitize reports before they are shared
- support optional aliases configured by the user

