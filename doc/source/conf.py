import sphinx_rtd_theme
from _version import get_versions

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "shellmarks"
copyright = "2019, Josef Friedrich"
author = "Josef Friedrich"
version = get_versions()["version"]
release = get_versions()["version"]
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False
html_static_path = []
htmlhelp_basename = "shellmarksdoc"
autodoc_default_flags = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
]
