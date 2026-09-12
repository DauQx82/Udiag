# udiag

Personal Ubuntu diagnostic tool written in Python,
with possible future support for other GNU/Linux distributions.

## Goal

Provide repeatable diagnostic modes without needing to remember
individual Linux commands.

## Current structure

- `udiag.py` - main CLI
- `mode_manager.py` - mode discovery/loading
- `config/` - system diagnostic modes
- `config/user/` - user environment diagnostic modes

## Status

Early prototype.
