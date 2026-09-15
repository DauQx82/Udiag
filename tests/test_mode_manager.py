from pathlib import Path
import pytest

from mode_manager import (scan_config,
						  validate_json,
						  validate_mode_structure,
						  validate_operation_structure)

def test_scan_config():
	test_list = scan_config()
	assert test_list != []

def test_validate_json():
	INVALID_PATH = Path(__file__).resolve().parent / "invalid"
	INVALID_SYNTAX = INVALID_PATH / "01-invalid-json-syntax.json"

	assert validate_json(INVALID_SYNTAX) is False

@pytest.mark.parametrize(
		"mode",
		[
			# No name
			{
				"description":"Missing name",
				"operations":[]
			},
			# mode_name_is_not_str
			{
				"name":42,
				"description":"Name is not a string",
				"operations":[]
			},
			# no_description
			{
				"name":"missing-description",
				"operations":[]
			},
			# no_operations
			{
				"name":"missing-operations",
				"description":"Operations field is missing"
			},
			# operations_is_not_list
			{
				"name":"operations-not-list",
				"description":"Operations is an object",
				"operations":{}
			},
			# operations_is_not_object
			{
				"name":"operation-not-object",
				"description":"Operation is a string",
				"operations":["not-an-object"]
			}
		]
)
def test_validate_mode_structure(mode):
	assert validate_mode_structure(mode) is False #type: ignore[arg-type]

@pytest.mark.parametrize(
	"operation",
	[
		# Missing title
		{
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": "equals",
			"expected": "running"
		},

		# Title is not str
		{
			"title": 42,
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": "equals",
			"expected": "running"
		},

		# Missing program
		{
			"title": "System state",
			"args": ["is-system-running"],
			"handler": "equals",
			"expected": "running"
		},

		# Program is not str
		{
			"title": "System state",
			"program": 42,
			"args": ["is-system-running"],
			"handler": "equals",
			"expected": "running"
		},

		# Missing args
		{
			"title": "System state",
			"program": "systemctl",
			"handler": "equals",
			"expected": "running"
		},

		# Args is not list
		{
			"title": "System state",
			"program": "systemctl",
			"args": "is-system-running",
			"handler": "equals",
			"expected": "running"
		},

		# Args contains non-string
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running", 42],
			"handler": "equals",
			"expected": "running"
		},

		# Missing handler
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running"],
			"expected": "running"
		},

		# Handler is not str
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": 42,
			"expected": "running"
		},

		# Equals without expected
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": "equals"
		},

		# Contains without expected
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": "contains"
		},

		# Expected is not str
		{
			"title": "System state",
			"program": "systemctl",
			"args": ["is-system-running"],
			"handler": "equals",
			"expected": 42
		},
	]
)
def test_invalid_operations(operation):
	assert validate_operation_structure(operation) is False  # type: ignore[arg-type]

