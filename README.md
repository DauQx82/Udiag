# udiag

Personal Ubuntu diagnostic tool written in Python,
with possible future support for other GNU/Linux distributions.

## Goal

Provide repeatable diagnostic modes without needing to remember
individual Linux commands.

Diagnostic modes are defined in JSON files and loaded dynamically.

## Current structure

- `udiag.py` - original working prototype
- `new_udiag.py` - JSON-driven CLI prototype
- `mode_manager.py` - mode discovery, loading and basic validation
- `modes/` - diagnostic mode definitions

## Current features

- discovers diagnostic modes from JSON files
- validates JSON syntax
- validates basic mode structure
- dynamically creates CLI arguments from mode definitions
- selects modes through `argparse`
- reads and executes operations defined in JSON

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
The current goal is to build a simple and predictable
JSON-driven diagnostic system before adding more advanced
result interpretation.

## Example

```bash

python3 new_udiag.py --base

```