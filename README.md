# udiag

Personal Ubuntu diagnostic tool written in Python,
with possible future support for other GNU/Linux distributions.

## Goal

Provide repeatable diagnostic modes without needing to remember
individual Linux commands.

Diagnostic modes are defined in JSON files and loaded dynamically.

## Current structure

- `udiag.py` - original working prototype
- `new_udiag.py` - current JSON-driven prototype
- `mode_manager.py` - mode discovery, loading and structural validation
- `modes/` - JSON diagnostic mode definitions

## Current features

- discovers diagnostic modes from JSON files
- validates JSON syntax
- validates mode structure
- validates individual operation structures
- uses typed `ModeDict` and `OperationDict` schemas
- dynamically creates CLI arguments and aliases from mode definitions
- reports invalid or unavailable modes
- selects modes through `argparse`
- creates and executes diagnostic operations
- captures stdout, stderr and process return codes

## Example flow

JSON mode
    ↓
argparse
    ↓
selected mode
    ↓
operations
    ↓
system command

## Status

Early prototype.

The current focus is to define and validate a consistent
JSON protocol for diagnostic modes and operations before
adding result interpreters and output sanitization.

## Example

```bash
python3 new_udiag.py --base
