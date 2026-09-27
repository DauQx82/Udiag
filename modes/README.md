# Modes and scenarios

A mode is a declarative diagnostic scenario stored as a JSON file. It describes
which programs Udiag should run and which conditions their results must satisfy.
The current code uses the word `mode` in the CLI and Python types; in this
document, *mode* and *scenario* refer to the same thing.

Udiag discovers `*.json` files directly inside the `modes/` directory. Nested
directories are not scanned. Each file is loaded and validated when Udiag
starts. Only modes containing at least one valid operation are made available
to the CLI.

## JSON format

A mode is a JSON object with three required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `name` | string | CLI name used by commands such as `udiag.py run <name>`. |
| `description` | string | Human-readable description shown by `list` and in the run header. |
| `operations` | non-empty array | Ordered operations executed by the mode. |

Each operation is an object with the following required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `title` | string | Human-readable operation name shown in terminal output. |
| `program` | non-empty string | Executable name or path passed directly to `subprocess.run()`. |
| `args` | array of strings | Command-line arguments. Use an empty array when no arguments are needed. |
| `checks` | non-empty object | Conditions evaluated against the completed process result. |

`program` and `args` do not use a shell. Pipes, redirects, variable expansion,
and other shell syntax are not interpreted. Each argument must be a separate
string in `args`.

Operations currently have a fixed execution timeout of 10 seconds. A missing
program, a permission error, or a timeout produces an execution error rather
than a failed check.

## The `source -> handler -> config` model

After a program finishes normally, Udiag creates an operation result containing
three data sources:

| Source | Runtime type | Value |
| --- | --- | --- |
| `stdout` | string | Text written to standard output. |
| `stderr` | string | Text written to standard error. |
| `returncode` | integer | Process exit code. |

The `checks` object maps each selected source to one or more handlers:

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

This is read as:

- take `stdout`, evaluate it with the `equals` handler, and pass `"running"`
  as the handler configuration;
- take `stderr`, evaluate it with the `empty` handler, and pass `true` as its
  configuration;
- take `returncode`, evaluate it with `equals`, and pass `0` as its
  configuration.

The engine selects the source value. The handler only receives that value as
`actual` and the JSON value as `config`. The meaning and accepted type of
`config` belong to the selected handler. See
[`handlers/README.md`](../handlers/README.md) for the current handlers and their
configuration contracts.

Different handlers may be declared for the same source:

```json
"stdout": {
    "equals": "ready",
    "contains": "read"
}
```

Every declared check is evaluated. An operation succeeds only when all its
checks succeed. A check mismatch is a normal failure, not an execution error.
A non-zero `returncode` has no automatic meaning: it succeeds or fails only
according to the checks declared by the scenario.

Because handlers are keys in a JSON object, the same handler name cannot appear
twice under one source.

## Example: checking all process result sources

```json
{
    "name": "python-check",
    "description": "Small Python runtime check",
    "operations": [
        {
            "title": "Print a known value",
            "program": "python3",
            "args": ["-c", "print('ready')"],
            "checks": {
                "stdout": {
                    "equals": "ready",
                    "contains": "read"
                },
                "stderr": {
                    "empty": true
                },
                "returncode": {
                    "equals": 0
                }
            }
        }
    ]
}
```

For text equality, the current `equals` handler removes only trailing `\r` and
`\n` characters from the actual value. It does not remove other whitespace.

## Example: informational output

```json
{
    "name": "kernel-info",
    "description": "Display kernel information",
    "operations": [
        {
            "title": "Read kernel details",
            "program": "uname",
            "args": ["-a"],
            "checks": {
                "stdout": {
                    "pass": true
                },
                "returncode": {
                    "equals": 0
                }
            }
        }
    ]
}
```

The `pass` handler always succeeds and preserves the selected value for detailed
terminal output. Here, `returncode` is still checked independently.

## Adding a mode

1. Create a new `*.json` file directly inside `modes/`.
2. Add the required top-level fields: `name`, `description`, and a non-empty
   `operations` array.
3. For each operation, define `title`, `program`, `args`, and a non-empty
   `checks` object.
4. Select one or more supported sources: `stdout`, `stderr`, or `returncode`.
5. Under each source, use handler names discovered from the `handlers/`
   directory and provide configuration accepted by those handlers.
6. Run `python3 udiag.py --errors` and correct any reported configuration
   problems.
7. Use `python3 udiag.py list` to confirm that the mode is available, then
   inspect or run it with:

   ```text
   python3 udiag.py show <name>
   python3 udiag.py run <name>
   python3 udiag.py run <name> --details
   ```

The JSON filename does not define the CLI name; the value of the `name` field
does.

## Validation rules and common errors

Udiag applies validation before executing a mode:

- the file must contain valid JSON and its root value must be an object;
- `name` and `description` must be strings;
- `operations` must be a non-empty array whose elements are objects;
- every operation must contain fields of the documented types;
- `program` cannot be empty or whitespace-only;
- every value in `args` must be a string;
- `checks` must be a non-empty object;
- only `stdout`, `stderr`, and `returncode` are accepted as sources;
- each selected source must contain a non-empty handler object;
- every handler name must exist in the runtime registry;
- every handler configuration must pass that handler's `validate_config()`.

If an operation object is invalid, Udiag reports it and keeps other valid
operation objects from the same mode. If no valid operations remain, the mode
is not exposed through the CLI. At the current validation boundary, a
non-object element inside `operations` invalidates the whole mode.

Common configuration mistakes include:

- using comments, trailing commas, or Python values such as `True` in JSON;
- writing a whole shell command in `program` instead of separating the
  executable and its arguments;
- using an unsupported source name;
- using a handler filename or class name instead of its registry name;
- passing a string such as `"0"` when a handler expects the integer `0`;
- passing `{}` as a source's handler mapping;
- using `false` with handlers whose configuration must be exactly `true`.

Only the documented fields are used when Udiag creates its validated runtime
structures. Do not rely on additional JSON fields being preserved.
