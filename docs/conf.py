# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.append(os.path.abspath("../src"))

# -- Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Alice RAG"
copyright = "2024"
author = "Philippe Miron"

# -- General configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.inheritance_diagram",
    "sphinx_copybutton",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output

html_theme = "sphinx_book_theme"
html_logo = "logo.webp"
html_favicon = "favicon.ico"
html_static_path: list[str] = []
