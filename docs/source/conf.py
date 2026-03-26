# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

project = "Toolbox_MLobs"
copyright = "2026, Lionel JOURDHIER"
author = "Lionel JOURDHIER"
release = "v0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # INDISPENSABLE : extrait la doc des docstrings
    "sphinx.ext.napoleon",  # Supporte le format Google/NumPy (plus lisible)
    "sphinx.ext.viewcode",  # Ajoute un lien [source] à côté de tes fonctions
    "sphinx.ext.mathjax",  # Pour le rendu des formules LaTeX
    "myst_parser",  # Pour lire les fichiers .md (README, etc.)
    "sphinxcontrib.bibtex",  # Pour la gestion du fichier .bib
]
templates_path = ["_templates"]

bibtex_bibfiles = ["refs.bib"]
exclude_patterns = []

language = "fr"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#7C4DFF",
        "color-brand-content": "#7C4DFF",
    },
}

bibtex_default_style = "unsrt"
