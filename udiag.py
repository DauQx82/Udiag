import os
import subprocess
import argparse
import sys
import pydoc # Na później 
# Trzeba dodać argumenty... 
# TODO Zastanowić się aby przenieść wynik do programu typu less, albo coś w tym stylu
# TODO Tui raczej jako konfiguracja, ewentualnie coś w tym stylu

def test() -> None:
	env_with_colors = os.environ.copy()
	env_with_colors["SYSTEMD_COLORS"] = "1"

	sub_list: list[str] = ["hostnamectl"]
	for i, process in enumerate(sub_list):
		result = subprocess.run([process], capture_output=True, text=True, env=env_with_colors)

		print(f"{1}. {process}")
		print(result.stdout)

		if result.stderr:
			print(f"Error: {result.stderr}")

#####################################################################

parser = argparse.ArgumentParser(description="Basic Diagnostic Systemm with args.")
# Basic diagnostic, informations.
parser.add_argument('--base', action='store_true', help='Basic Diagnostic')
# Package consistency
parser.add_argument('--pkg', action='store_true', help='Package Consistency')
# Updates 
parser.add_argument('--check-updates', action='store_true', help='Updates and Upgrades Diagnostic')
args = parser.parse_args()

base_diag_list: list[str] = [
	"hostnamectl",
	"uname -a",
	"df -h",
	"systemctl is-system-running",
	"systemctl --failed --no-pager",
	"systemctl --user --failed --no-pager"
]
pkg_base_diag_list: list[str] = [
	"dpkg --audit",
	"apt-mark showhold"
]
check_update_base_diag_list: list[str] = [
	"sudo apt update",
	"apt list --upgradable 2>/dev/null",
	"apt-get -s upgrade",

]

def base_diagnostic(cmd_list: list[str]) -> None:
	"""Basic diagnostic system result loop"""
	for i, process in enumerate(cmd_list, start=1):
		print(f"\n\033[1;32m=== {i}. {process} ===\033[0m")

		subprocess.run(process, shell=True)

		print("\n" + "#"*40)

def open_config_file() -> None:
	"""Future, after test."""
	...

def appinfo() -> None:
	parser.print_help()
if __name__ == "__main__":
	if len(sys.argv) == 1:
		appinfo()
		sys.exit()

	if args.base:
		base_diagnostic(base_diag_list)
	if args.pkg:
		base_diagnostic(pkg_base_diag_list)
	if args.check_updates:
		base_diagnostic(check_update_base_diag_list)


