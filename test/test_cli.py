"""Test the CLI"""

import os
import filecmp
import pdb

import pytest

def test_cli():
    exit_status = os.system('python -m manyworlds --help')
    assert exit_status == 0
