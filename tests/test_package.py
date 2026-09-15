"""Smoke tests for the Phase 1 package layout. No application logic."""

from again import __version__


def test_package_version():
    assert __version__ == "0.1.0"
