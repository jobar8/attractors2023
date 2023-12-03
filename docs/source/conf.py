"""Configuration file for the Sphinx documentation builder."""
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import pathlib
import sys

# pylint: disable=invalid-name

sys.path.insert(0, (pathlib.Path(__file__).parents[2].resolve() / 'src').as_posix())

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Attractors 2023'
author = 'Joseph Barraud'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# Note: the order of the extensions matters!

extensions = [
    'sphinx.ext.autodoc',  # Core Sphinx library for auto doc generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables for modules/classes/methods etc
    'sphinx.ext.intersphinx',  # Link to other project's documentation (see mapping below)
    'numpydoc',
]

templates_path = ['_templates']
exclude_patterns = []
root_doc = 'index'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Remove 'view source code' from top of page (for html, not python)
html_show_sourcelink = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_css_files = ['pydata-custom.css']
html_static_path = ['_static']


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'navigation_depth': 2,
    'show_toc_level': 2,
}

# -- Options for autodoc ------------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',  # instead of alphabetical
    'inherited-members': False,  # it would show docs of DataFrame if True
    'exclude-members': 'set_output',
    'private-members': True,
}

# use 'both' to show the description of the __init__ method
autoclass_content = 'both'

# Show typehints as content of the function or method (identical as loading sphinx_autodoc_typehints extension)
autodoc_typehints = 'description'

# Always add return type with 'documented_params'
autodoc_typehints_description_target = 'documented_params'

# Apparently the same as the "inherited-members" option above
autodoc_inherit_docstrings = False

# Not used because the doc is built into its own venv
# autodoc_mock_imports = ["pandas", "numpy", "s3path", "tqdm", "ruamel", "boto3", "botocore"]

# generate autosummary even if no references
autosummary_generate = True

# -- Options for numpydoc -----------------------------------------------------
# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_show_class_members = False
numpydoc_validation_checks = {'all', 'GL01', 'SS06', 'EX01', 'SA01', 'YD01', 'ES01', 'RT01'}
numpydoc_validation_overrides = {
    'SS05': [  # override SS05 to allow docstrings starting with these words
        '^Process ',
        '^Assess ',
        '^Access ',
        '^Compress ',
        '^Decompress ',
    ]
}

# -- Options for intersphinx --------------------------------------------------
# This makes for example numpy types clickable

intersphinx_mapping = {
    'python': (f'https://docs.python.org/{sys.version_info.major}', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'sklearn': ('https://scikit-learn.org/stable', None),
}
