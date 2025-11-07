"""
Test CLI

Validates CLI argument parsing and subcommand execution for rsvp_analysis_suite.
"""

import subprocess
import sys
import os


def test_cli_help():
    result = subprocess.run([sys.executable, 'cli.py', '--help'], capture_output=True, text=True)
    assert result.returncode == 0, "CLI help failed"
    assert 'usage' in result.stdout.lower(), "CLI help output missing usage"


def test_cli_subcommand():
    # Example: test a dry-run subcommand (replace with actual subcommand)
    subcommand = 'simulate'  # adjust to a real CLI subcommand
    result = subprocess.run([sys.executable, 'cli.py', subcommand, '--dry-run'], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI subcommand {subcommand} failed"


if __name__ == '__main__':
    test_cli_help()
    print('CLI help test passed.')
    # Commented out if subcommand not implemented
    # test_cli_subcommand()
    # print('CLI subcommand test passed.')

