import datetime

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "finam_plot"
copyright = f"2021 - {datetime.datetime.now().year}, Team LandTECH"
author = "FINAM Developers"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # parameters look better than with numpydoc only
    "numpydoc",
]

# autosummaries from source-files
autosummary_generate = True
# dont show __init__ docstring
autoclass_content = "class"
# for uniqur labels/anchors
autosectionlabel_prefix_document = True
# sort class members
autodoc_member_order = "groupwise"
# autodoc_member_order = 'bysource'

# Notes in boxes
napoleon_use_admonition_for_notes = True
# Attributes like parameters
napoleon_use_ivar = True
# keep "Other Parameters" section
# https://github.com/sphinx-doc/sphinx/issues/10330
napoleon_use_param = False
# this is a nice class-doc layout
numpydoc_show_class_members = True
# class members have no separate file, so they are not in a toctree
numpydoc_class_members_toctree = False
# maybe switch off with:    :no-inherited-members:
numpydoc_show_inherited_class_members = True
# add refs to types also in parameter lists
numpydoc_xref_param_type = True

myst_enable_extensions = [
    "colon_fence",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]

html_logo = "_static/logo_large.svg"
html_favicon = "_static/logo.svg"

html_theme_options = {
    "secondary_sidebar_items": ["page-toc"],
    "footer_start": ["copyright"],
    "show_nav_level": 2,
    "show_toc_level": 2,
    "icon_links": [
        {
            "name": "Source code",
            "url": "https://git.ufz.de/FINAM/finam-plot",
            "icon": "fa-brands fa-square-gitlab",
            "type": "fontawesome",
            "attributes": {"target": "_blank"},
        },
        {
            "name": "FINAM homepage",
            "url": "https://finam.pages.ufz.de",
            "icon": "_static/logo.svg",
            "type": "local",
            "attributes": {"target": "_blank"},
        },
    ],
    "external_links": [
        {"name": "FINAM documentation", "url": "https://finam.pages.ufz.de/finam"},
    ],
}

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "Python": ("https://docs.python.org/", None),
    "NumPy": ("http://docs.scipy.org/doc/numpy/", None),
    "matplotlib": ("http://matplotlib.org/stable/", None),
    "pytest": ("https://docs.pytest.org/en/7.1.x/", None),
    "finam": ("https://finam.pages.ufz.de/finam/", None),
}
