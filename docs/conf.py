"""Sphinx configuration."""

from datetime import datetime


project = "inquirer"
author = "Miguel Ángel García"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
