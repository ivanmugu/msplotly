"""Miscellaneous functions.

License
-------
This file is part of MSPlotly
BSD 3-Clause License
Copyright (c) 2024, Ivan Munoz Gutierrez
"""

import importlib.resources as resources
from pathlib import Path


def get_package_path(package: str = "msplotly") -> Path:
    """Get path to package directory in a src-layout"""
    return resources.files(f"{package}")


if __name__ == "__main__":
    print(get_package_path())
