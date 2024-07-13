import sys

sys.setrecursionlimit(30000)

# import sphinx_rtd_theme
from docutils import nodes
from docutils.parsers.rst import roles

# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "KFRE"
copyright = "2024, Leonid Shpaner"
author = "Leonid Shpaner"
release = "0.1.8"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}

html_static_path = ["_static"]
html_show_sourcelink = False

# Example of setting a Pygments style for syntax highlighting
pygments_style = "default"


def bold_italic(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.strong(text=text)
    node.children = [nodes.emphasis(text=text)]
    return [node], []


roles.register_local_role("bolditalic", bold_italic)

html_css_files = [
    "custom.css",
]
