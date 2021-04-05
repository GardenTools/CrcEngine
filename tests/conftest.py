"""Pytest test configuration"""
import pytest


def pytest_addoption(parser):
    parser.addoption("--no-ceedling", action="store_true", help="run slow tests")


def pytest_configure(config):
    # Add the needs_ceedling marker as though it had been defined in pytest.ini
    config.addinivalue_line(
        "markers", "needs_ceedling: mark test as requiring ceedling"
    )


def pytest_collection_modifyitems(config, items):
    # If a test has the needs_ceedling marker and no-ceedling has been specified
    # mark it as a skipped test
    print("beep")
    if config.getoption("--no-ceedling"):
        print("no ceedling")
        skip_ceedling = pytest.mark.skip(reason="--no-ceedling specified")
        for item in items:
            if "needs_ceedling" in item.keywords:
                item.add_marker(skip_ceedling)
