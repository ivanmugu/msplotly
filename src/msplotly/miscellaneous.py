"""Miscellaneous functions."""

import importlib.resources as resources
from pathlib import Path


def get_package_path(package: str = "msplotly") -> Path:
    """Get path to package directory in a src-layout"""
    return resources.files(f"{package}")
